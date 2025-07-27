"""
Unit tests for the Concordance API
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import os
import time
from unittest.mock import patch

from concordance_api import app, load_corpus, tokenize_line, search_kwic, KWICResult

client = TestClient(app)


class TestAPI:
    """Test API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns HTML frontend"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Concordancer" in response.text
    
    def test_list_corpora_endpoint(self):
        """Test corpora listing endpoint"""
        response = client.get("/corpora")
        assert response.status_code == 200
        data = response.json()
        assert "corpora" in data
        assert isinstance(data["corpora"], list)


class TestCorpusLoading:
    """Test corpus loading functionality"""
    
    def test_load_corpus_missing_file(self):
        """Test loading non-existent corpus raises HTTPException"""
        with pytest.raises(Exception):  # HTTPException
            load_corpus("nonexistent_corpus")
    
    def test_load_corpus_with_temp_file(self):
        """Test loading corpus from temporary file"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is line one.\n")
            f.write("This is line two.\n")
            f.write("This is line three.\n")
            temp_path = f.name
        
        try:
            # Move to samples directory structure
            samples_dir = Path("samples")
            samples_dir.mkdir(exist_ok=True)
            
            test_corpus_path = samples_dir / "test_corpus.txt"
            Path(temp_path).rename(test_corpus_path)
            
            # Test loading
            lines = load_corpus("test_corpus")
            assert len(lines) == 3
            assert lines[0] == "This is line one."
            assert lines[1] == "This is line two."
            assert lines[2] == "This is line three."
            
        finally:
            # Cleanup
            if test_corpus_path.exists():
                test_corpus_path.unlink()


class TestTokenization:
    """Test tokenization functionality"""
    
    def test_tokenize_simple_sentence(self):
        """Test basic tokenization"""
        tokens = tokenize_line("Hello world!")
        assert tokens == ["Hello", "world", "!"]
    
    def test_tokenize_with_punctuation(self):
        """Test tokenization with various punctuation"""
        tokens = tokenize_line("Hello, world! How are you?")
        assert tokens == ["Hello", ",", "world", "!", "How", "are", "you", "?"]
    
    def test_tokenize_empty_string(self):
        """Test tokenization of empty string"""
        tokens = tokenize_line("")
        assert tokens == []
    
    def test_tokenize_with_numbers(self):
        """Test tokenization with numbers"""
        tokens = tokenize_line("I have 5 apples and 10 oranges.")
        assert "5" in tokens
        assert "10" in tokens


class TestKWICSearch:
    """Test KWIC search functionality"""
    
    def test_search_kwic_exact_match(self):
        """Test KWIC search with exact match"""
        tokens = ["The", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"]
        result = search_kwic(tokens, "fox", context_size=2)
        
        assert result is not None
        assert isinstance(result, KWICResult)
        assert result.left == ["quick", "brown"]
        assert result.match == ["fox"]
        assert result.right == ["jumps", "over"]
    
    def test_search_kwic_case_insensitive(self):
        """Test KWIC search is case insensitive"""
        tokens = ["The", "Quick", "Brown", "Fox"]
        result = search_kwic(tokens, "fox", context_size=1)
        
        assert result is not None
        assert result.match == ["Fox"]  # Original case preserved
    
    def test_search_kwic_no_match(self):
        """Test KWIC search with no match"""
        tokens = ["The", "quick", "brown", "fox"]
        result = search_kwic(tokens, "elephant", context_size=2)
        
        assert result is None
    
    def test_search_kwic_edge_cases(self):
        """Test KWIC search at edges of token list"""
        tokens = ["first", "middle", "last"]
        
        # Match at beginning
        result = search_kwic(tokens, "first", context_size=5)
        assert result.left == []
        assert result.match == ["first"]
        assert result.right == ["middle", "last"]
        
        # Match at end
        result = search_kwic(tokens, "last", context_size=5)
        assert result.left == ["first", "middle"]
        assert result.match == ["last"]
        assert result.right == []
    
    def test_search_kwic_small_context(self):
        """Test KWIC search with small context size"""
        tokens = ["a", "b", "c", "d", "e", "f", "g"]
        result = search_kwic(tokens, "d", context_size=1)
        
        assert result.left == ["c"]
        assert result.match == ["d"]
        assert result.right == ["e"]


class TestSearchEndpoint:
    """Test search endpoint integration"""
    
    def test_search_missing_corpus(self):
        """Test search with missing corpus parameter"""
        response = client.get("/search?query=test")
        assert response.status_code == 422  # Validation error
    
    def test_search_missing_query(self):
        """Test search with missing query parameter"""
        response = client.get("/search?corpus=test")
        assert response.status_code == 422  # Validation error
    
    def test_search_empty_query(self):
        """Test search with empty query"""
        response = client.get("/search?corpus=test&query=")
        assert response.status_code == 400
    
    def test_search_nonexistent_corpus(self):
        """Test search with non-existent corpus"""
        response = client.get("/search?corpus=nonexistent&query=test")
        assert response.status_code == 404


class TestFileViewingEndpoints:
    """Test file viewing and search endpoints"""
    
    def test_view_file_missing_corpus(self):
        """Test view file with non-existent corpus"""
        response = client.get("/view/nonexistent")
        assert response.status_code == 404
    
    def test_view_file_with_temp_file(self):
        """Test viewing file content with temporary file"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Line one\nLine two\nLine three")
            temp_path = f.name
        
        try:
            # Move to samples directory
            samples_dir = Path("samples")
            samples_dir.mkdir(exist_ok=True)
            
            test_corpus_path = samples_dir / "test_view.txt"
            Path(temp_path).rename(test_corpus_path)
            
            # Test file viewing
            response = client.get("/view/test_view")
            assert response.status_code == 200
            
            data = response.json()
            assert data["filename"] == "test_view.txt"
            assert data["line_count"] == 3
            assert data["word_count"] == 6
            assert "Line one" in data["content"]
            
        finally:
            # Cleanup
            if test_corpus_path.exists():
                test_corpus_path.unlink()
    
    def test_search_in_file_missing_corpus(self):
        """Test search in non-existent file"""
        response = client.get("/search-in-file/nonexistent?query=test")
        assert response.status_code == 404
    
    def test_search_in_file_empty_query(self):
        """Test search in file with empty query"""
        response = client.get("/search-in-file/test?query=")
        assert response.status_code == 400
    
    def test_search_in_file_with_temp_file(self):
        """Test searching within file with temporary file"""
        # Create temporary file with searchable content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("The quick brown fox\nThe lazy dog\nFox jumps over")
            temp_path = f.name
        
        try:
            # Move to samples directory
            samples_dir = Path("samples")
            samples_dir.mkdir(exist_ok=True)
            
            test_corpus_path = samples_dir / "test_search.txt"
            Path(temp_path).rename(test_corpus_path)
            
            # Test search in file
            response = client.get("/search-in-file/test_search?query=fox")
            assert response.status_code == 200
            
            data = response.json()
            assert data["query"] == "fox"
            assert data["case_sensitive"] is False
            assert data["total_lines_matched"] == 2  # "fox" appears in 2 lines (case insensitive)
            assert len(data["results"]) == 2
            
            # Test case sensitive search
            response = client.get("/search-in-file/test_search?query=Fox&case_sensitive=true")
            assert response.status_code == 200
            
            data = response.json()
            assert data["case_sensitive"] is True
            assert data["total_lines_matched"] == 1  # Only "Fox" with capital F
            
        finally:
            # Cleanup
            if test_corpus_path.exists():
                test_corpus_path.unlink()


class TestPerformance:
    """Performance benchmarking tests"""
    
    @pytest.fixture
    def large_corpus_file(self):
        """Create a large test corpus for performance testing"""
        samples_dir = Path("samples")
        samples_dir.mkdir(exist_ok=True)
        
        large_file = samples_dir / "perf_test_large.txt"
        
        # Create a corpus with 1000 lines of varied text
        lines = []
        base_words = ["the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog", "and", "runs", "through", "forest"]
        
        for i in range(1000):
            # Vary line length and content
            line_words = base_words * (i % 5 + 1)  # 12 to 60 words per line
            line = " ".join(line_words) + f" line{i}"
            lines.append(line)
        
        content = "\n".join(lines)
        large_file.write_text(content, encoding='utf-8')
        
        yield "perf_test_large"
        
        # Cleanup
        if large_file.exists():
            large_file.unlink()
    
    def test_corpus_loading_performance(self, large_corpus_file):
        """Test corpus loading performance with timing"""
        start_time = time.time()
        lines = load_corpus(large_corpus_file)
        load_time = time.time() - start_time
        
        assert len(lines) == 1000
        assert load_time < 1.0  # Should load in under 1 second
        print(f"\nCorpus loading time: {load_time:.3f}s for {len(lines)} lines")
    
    def test_search_performance_common_word(self, large_corpus_file):
        """Test search performance with a common word"""
        # Pre-load corpus
        load_corpus(large_corpus_file)
        
        start_time = time.time()
        response = client.get(f"/search?corpus={large_corpus_file}&query=the")
        search_time = time.time() - start_time
        
        assert response.status_code == 200
        data = response.json()
        
        assert search_time < 2.0  # Should complete in under 2 seconds
        assert data["total_hits"] > 0
        print(f"\nSearch time: {search_time:.3f}s for {data['total_hits']} hits")
    
    def test_search_performance_rare_word(self, large_corpus_file):
        """Test search performance with a rare word"""
        start_time = time.time()
        response = client.get(f"/search?corpus={large_corpus_file}&query=line999")
        search_time = time.time() - start_time
        
        assert response.status_code == 200
        data = response.json()
        
        assert search_time < 1.0  # Rare word should be faster
        assert data["total_hits"] == 1
        print(f"\nRare word search time: {search_time:.3f}s")
    
    def test_multiple_searches_same_corpus(self, large_corpus_file):
        """Test repeated searches on same corpus (should benefit from caching)"""
        # First search
        start_time = time.time()
        response1 = client.get(f"/search?corpus={large_corpus_file}&query=fox")
        first_time = time.time() - start_time
        
        # Second search (should be faster due to caching)
        start_time = time.time()
        response2 = client.get(f"/search?corpus={large_corpus_file}&query=dog")
        second_time = time.time() - start_time
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        print(f"\nFirst search: {first_time:.3f}s, Second search: {second_time:.3f}s")
        # Note: Second search might be faster due to file being in OS cache
    
    def test_tokenization_performance(self):
        """Test tokenization performance on long lines"""
        # Create a very long line (1000 words)
        long_line = " ".join(["word"] * 1000)
        
        start_time = time.time()
        for _ in range(100):  # Tokenize 100 times
            tokens = tokenize_line(long_line)
        tokenize_time = time.time() - start_time
        
        assert len(tokens) == 1000
        assert tokenize_time < 1.0  # 100 tokenizations should complete in under 1 second
        print(f"\nTokenization time: {tokenize_time:.3f}s for 100 iterations")


class TestPaginationAndCaching:
    """Test pagination and caching features"""
    
    def test_search_pagination(self):
        """Test search pagination functionality"""
        # Search with small page size
        response = client.get("/search?corpus=AllsWellThatEndsWell&query=the&page_size=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert len(data["results"]) <= 5
        assert data["total_hits"] >= len(data["results"])
        assert data["total_pages"] >= 1
        
        # Test second page if available
        if data["total_pages"] > 1:
            response2 = client.get("/search?corpus=AllsWellThatEndsWell&query=the&page=2&page_size=5")
            assert response2.status_code == 200
            
            data2 = response2.json()
            assert data2["page"] == 2
            assert data2["total_hits"] == data["total_hits"]  # Same total
    
    def test_pagination_invalid_page(self):
        """Test pagination with invalid page number"""
        response = client.get("/search?corpus=AllsWellThatEndsWell&query=the&page=999999")
        assert response.status_code == 400
    
    def test_cache_status_endpoint(self):
        """Test cache status endpoint"""
        # Perform a search to populate cache
        client.get("/search?corpus=AllsWellThatEndsWell&query=King")
        
        # Check cache status
        response = client.get("/cache/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "cached_corpora" in data
        assert "total_memory_mb" in data
        assert "cache_details" in data
        assert data["cached_corpora"] >= 1
        assert "AllsWellThatEndsWell" in data["cache_details"]
        
        # Check corpus-specific metadata
        corpus_info = data["cache_details"]["AllsWellThatEndsWell"]
        assert "line_count" in corpus_info
        assert "memory_mb" in corpus_info
        assert "access_count" in corpus_info
        assert corpus_info["access_count"] >= 1
    
    def test_cache_clear_specific(self):
        """Test clearing cache for specific corpus"""
        # Populate cache
        client.get("/search?corpus=AllsWellThatEndsWell&query=test")
        
        # Clear specific corpus
        response = client.post("/cache/clear?corpus=AllsWellThatEndsWell")
        assert response.status_code == 200
        
        # Verify it's cleared
        status_response = client.get("/cache/status")
        data = status_response.json()
        assert "AllsWellThatEndsWell" not in data["cache_details"]
    
    def test_cache_clear_all(self):
        """Test clearing all cache"""
        # Populate cache with multiple corpora
        client.get("/search?corpus=AllsWellThatEndsWell&query=test")
        client.get("/search?corpus=Enron_email&query=test")
        
        # Clear all cache
        response = client.post("/cache/clear")
        assert response.status_code == 200
        
        # Verify all cleared
        status_response = client.get("/cache/status")
        data = status_response.json()
        assert data["cached_corpora"] == 0
        assert data["cache_details"] == {}


class TestRealCorpusIntegration:
    """Integration tests using real corpus files"""
    
    def test_shakespeare_corpus_search(self):
        """Test search functionality with Shakespeare corpus"""
        response = client.get("/search?corpus=AllsWellThatEndsWell&query=King")
        assert response.status_code == 200
        
        data = response.json()
        assert data["corpus"] == "AllsWellThatEndsWell"
        assert data["query"] == "King"
        assert data["total_hits"] > 0
        assert len(data["results"]) == data["total_hits"]
        
        # Verify KWIC structure
        for result in data["results"][:5]:  # Check first 5 results
            assert isinstance(result["left"], list)
            assert isinstance(result["match"], list)
            assert isinstance(result["right"], list)
            assert result["match"] == ["King"]  # Exact match preserved
            assert result["line_number"] > 0
    
    def test_wikipedia_corpus_search(self):
        """Test search with Wikipedia corpus"""
        response = client.get("/search?corpus=wikipedia_corpus_sample&query=the&context_size=3")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_hits"] > 0
        
        # Check context size is respected
        for result in data["results"][:3]:
            assert len(result["left"]) <= 3
            assert len(result["right"]) <= 3
    
    def test_enron_email_corpus(self):
        """Test search with Enron email corpus"""
        response = client.get("/search?corpus=Enron_email&query=meeting")
        assert response.status_code == 200
        
        data = response.json()
        # May or may not find matches depending on content
        assert isinstance(data["results"], list)
    
    def test_large_context_search(self):
        """Test search with large context size"""
        response = client.get("/search?corpus=AllsWellThatEndsWell&query=Lord&context_size=10")
        assert response.status_code == 200
        
        data = response.json()
        if data["total_hits"] > 0:
            # Verify larger context
            result = data["results"][0]
            total_context = len(result["left"]) + len(result["right"])
            assert total_context <= 20  # Max 10 left + 10 right


if __name__ == "__main__":
    pytest.main([__file__])
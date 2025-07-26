"""
Unit tests for the Concordance API
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import os

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


if __name__ == "__main__":
    pytest.main([__file__])
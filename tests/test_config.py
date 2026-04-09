from src.config import Config
import pytest

def test_config_fails_if_bucket_not_set(monkeypatch):
    original_instance = Config._instance
    
    try:
        monkeypatch.delenv("S3_BUCKET_NAME", raising=False)
        Config._instance = None

        with pytest.raises(ValueError) as exc_info:
            Config()

        assert "S3_BUCKET_NAME" in str(exc_info.value)

    finally:
        Config._instance = original_instance

def test_config_fails_if_parts_url_not_set(monkeypatch):
    original_instance = Config._instance
    
    try:
        monkeypatch.delenv("REBRICKABLE_PARTS_CSV_URL", raising=False)
        Config._instance = None

        with pytest.raises(ValueError) as exc_info:
            Config()

        assert "REBRICKABLE_PARTS_CSV_URL" in str(exc_info.value)

    finally:
        Config._instance = original_instance

def test_config_fails_if_categories_url_not_set(monkeypatch):
    original_instance = Config._instance
    
    try:
        monkeypatch.delenv("REBRICKABLE_CATEGORIES_CSV_URL", raising=False)
        Config._instance = None

        with pytest.raises(ValueError) as exc_info:
            Config()

        assert "REBRICKABLE_CATEGORIES_CSV_URL" in str(exc_info.value)

    finally:
        Config._instance = original_instance

def test_config_manifest_path_fallbacks_to_default(monkeypatch):
    original_instance = Config._instance
    
    try:
        monkeypatch.delenv("MANIFEST_PATH", raising=False)
        Config._instance = None
        config = Config()
        assert config.MANIFEST_PATH == "manifest.json"

    finally:
        Config._instance = original_instance

def test_config_loads_correctly(monkeypatch):
    original_instance = Config._instance
    
    try:
        test_bucket = "test-bucket"
        test_manifest_path = "test-manifest.json"
        test_tmp_dir = "test-tmp"
        test_parts_url = "test-parts-url"
        test_categories_url = "test-categories-url"
        
        monkeypatch.setenv("S3_BUCKET_NAME", test_bucket)
        monkeypatch.setenv("MANIFEST_PATH", test_manifest_path)
        monkeypatch.setenv("TMP_DIR", test_tmp_dir)
        monkeypatch.setenv("REBRICKABLE_PARTS_CSV_URL", test_parts_url)
        monkeypatch.setenv("REBRICKABLE_CATEGORIES_CSV_URL", test_categories_url)
        
        Config._instance = None
        config = Config()
        
        assert config.S3_BUCKET == test_bucket
        assert config.MANIFEST_PATH == test_manifest_path
        assert config.TMP_DIR == test_tmp_dir
        assert config.RESOURCES == {
            "parts": test_parts_url,
            "categories": test_categories_url,
        }
        
    finally:
        Config._instance = original_instance

def test_get_required_env_var_success(monkeypatch):
    monkeypatch.setenv("TEST_KEY", "test_value")
    config = Config()
    assert config._get_required_env("TEST_KEY") == "test_value"

def test_get_required_env_var_fails_if_not_set(monkeypatch):
    monkeypatch.delenv("TEST_KEY", raising=False)
    config = Config()
    with pytest.raises(ValueError) as exc_info:
        config._get_required_env("TEST_KEY")
    assert "TEST_KEY" in str(exc_info.value)

def test_get_required_env_var_fails_if_empty_string(monkeypatch):
    monkeypatch.setenv("TEST_KEY", "")
    config = Config()
    with pytest.raises(ValueError) as exc_info:
        config._get_required_env("TEST_KEY")
    assert "TEST_KEY" in str(exc_info.value)
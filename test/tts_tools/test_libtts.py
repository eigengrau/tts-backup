import pytest


# seekURL ignores page URLs from a fixture.
@pytest.mark.skip
def test_seekURL_ignore_page_url():
    pass


# seekURL ignores tablet URLs from a fixture.
@pytest.mark.skip
def test_seekURL_ignore_tablet_url():
    pass


# seekURL returns audio library items from a fixture.
@pytest.mark.skip
def test_seekURL_extract_audio_library_item():
    pass


# seekURL ignores URL keys with no value from the fixture.
@pytest.mark.skip
def test_seekURL_ignore_empty_URL():
    pass


# seekURL strips in-band metadata (curly braces) from URLs.
@pytest.mark.skip
def test_seekURL_strip_url_inband_metadata():
    pass


# seekURL returns expected URLs for the fixture.
@pytest.mark.skip
def test_seekURL_return_common_url():
    pass


# is_obj selects expected mesh URLs from the fixture.
@pytest.mark.skip
def test_is_obj_mesh():
    pass


# is_obj selects expected collider URLs from the fixture.
@pytest.mark.skip
def test_is_obj_collider():
    pass


# is_obj filters anything else from the fixture.
@pytest.mark.skip
def test_is_obj_other():
    pass


# is_image selects expected image keys from the fixture.
@pytest.mark.skip
def test_is_image_known_image_keys():
    pass


# is_image filters anything else from the fixture.
@pytest.mark.skip
def test_is_image_non_image_keys():
    pass


# is_assetbundle selects asset-bundle keys from the fixture.
@pytest.mark.skip
def test_is_assetbundle_known_asset_bundle_keys():
    pass


# is_assetbundle filters anything else from the fixture.
@pytest.mark.skip
def test_is_assetbundle_non_assetbundle_keys():
    pass


# is_audiolibrary selects audio-library keys from the fixture.
@pytest.mark.skip
def test_is_audiolibrary_known_audiolibrary_keys():
    pass


# is_audiolibrary filters anything else from the fixture.
@pytest.mark.skip
def test_is_audiolibrary_non_audiolibrary_keys():
    pass


# is_pdf selects PDF keys from the fixture.
@pytest.mark.skip
def test_is_pdf_known_pdf_keys():
    pass


# is_pdf filters anything else from the fixture.
@pytest.mark.skip
def test_is_pdf_non_pdf_keys():
    pass


# recodeURL rewrites URLs as expected
@pytest.mark.skip
def test_recodeURL():
    pass


# get_fs_path returns cache paths as expected
@pytest.mark.skip
def test_get_fs_path():
    pass


# urls_from_save returns expected URLs from a save file fixture
@pytest.mark.skip
def test_urls_from_save():
    pass


# get_save_name extracts the save file name from a save file fixture
@pytest.mark.skip
def test_get_save_name():
    pass

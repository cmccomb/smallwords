from smallwords import WORDLISTS, get_wordlist


def test_source_backed_wordlists_are_available() -> None:
    assert {"common_50", "common_100", "common_250", "basic_850", "special_english", "reasoning_250"} <= WORDLISTS.keys()


def test_wordlist_provenance_and_sizes() -> None:
    common = get_wordlist("common_250")
    basic = get_wordlist("basic_850")
    special = get_wordlist("special_english")

    assert len(common.words) == 250
    assert common.source_name.startswith("Project Gutenberg Moby Words II")
    assert len(common.source_urls) == 2
    assert common.license_name == "Public domain + MIT"

    assert len(basic.words) == 850
    assert basic.source_name.startswith("Basic English 850")
    assert basic.license_name == "MIT"

    assert len(special.words) == 1475
    assert special.source_name.startswith("Voice of America Special English")
    assert special.license_name == "MIT"

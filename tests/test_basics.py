from smallwords import COMMON_50, is_compliant, out_of_vocab, prompt_explain_simply


def test_prompt_mentions_wordlist() -> None:
    prompt = prompt_explain_simply("How does rain work?", wordlist="common_50")
    assert "common_50" in prompt



def test_gbnf_has_root() -> None:
    assert COMMON_50.gbnf.startswith("root ::= text")



def test_validation() -> None:
    assert is_compliant("The man can make it.", "common_50")
    assert "bridge" in out_of_vocab("The man can make a bridge.", "common_50")

rule TestRule
{
    meta:
        author = "HP"

    strings:
        $str1 = "myniceteststring"
    condition:
        $str1
}

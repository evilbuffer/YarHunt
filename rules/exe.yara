rule exefile
{
    meta:
        author = "HP"

    strings:
        $str1 = "PE"
    condition:
        $str1

}
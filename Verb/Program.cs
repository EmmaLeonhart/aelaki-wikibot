using System;
using System.Collections.Generic;
using System.Text;

class Program
{
    static void Main()
    {
        string root = "kmdr";   // your 4-consonant root

        // name → patternOrLiteral
        var forms = new List<(string name, string pat)>()
        {
            ("Telic Perfect"      , "1-a-2-3-e-r"),
            ("Telic Imperfect"    , "1-a-2-3-o-r"),
            ("Atelic Perfect"     , "1-a-2-e-3-e-r"),
            ("Atelic Imperfect"   , "1-a-2-o-3-o-r"),
            ("Telic Perfect (n)"  , "kandeder"),             // literal
            ("Habitual Imperfect" , "1-a-2-3-o-3-o-4"),
            ("Telic Perfect**"    , "kandender"),            // literal
            ("Gnomic Imperfect"   , "1-a-2-3-a-2-3-o-4"),
            ("Atelic Perfect**"   , "kamedemeder"),          // literal
            ("Atelic Imperfect**" , "kamodomodor"),          // literal
            ("Imperative"         , "alakamadro"),           // literal
        };

        foreach (var (name, pat) in forms)
        {
            string output = pat.Contains("-")
                ? GenerateFromPattern(root, pat)
                : pat;

            Console.WriteLine($"{name.PadRight(20)} → {output}");
        }
    }

    // Reuses the same dash-parser: 1→k, 2→m, etc.
    static string GenerateFromPattern(string root, string pattern)
    {
        var sb = new StringBuilder();
        string[] tokens = pattern.Split('-');
        foreach (var t in tokens)
        {
            if (int.TryParse(t, out int idx) && idx >= 1 && idx <= root.Length)
                sb.Append(root[idx - 1]);
            else
                sb.Append(t);
        }
        return sb.ToString();
    }
}

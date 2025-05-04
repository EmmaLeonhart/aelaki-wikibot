using System;
using System.Collections.Generic;
using System.Text;

class Program
{
    static void Main()
    {
        // 1) Your 4-consonant root:
        string root = "kmdr";

        // 2) List your templates here:
        var templates = new Dictionary<string, string>
        {
            // key = a name/comment, value = the dash-pattern
            {"Telic Perfect",       "1-a-2-3-e-r"},
            {"Telic Imperfect",     "1-a-2-3-o-r"},
            {"Atelic Perfect",      "1-a-2-e-3-e-r"},
            {"Atelic Imperfect",    "1-a-2-o-3-o-r"},
            // add more here as needed...
        };

        // 3) Generate and print
        Console.WriteLine($"Root = {root}\n");
        foreach (var kv in templates)
        {
            string name = kv.Key;
            string pattern = kv.Value;
            string form = GenerateFromPattern(root, pattern);
            Console.WriteLine($"{name.PadRight(15)} => {form}");
        }
    }

    // Maps "1"→root[0], "2"→root[1], etc.; anything else is emitted literally.
    static string GenerateFromPattern(string root, string pattern)
    {
        var sb = new StringBuilder();
        string[] tokens = pattern.Split('-');
        foreach (var t in tokens)
        {
            if (int.TryParse(t, out int idx) && idx >= 1 && idx <= root.Length)
            {
                sb.Append(root[idx - 1]);
            }
            else
            {
                sb.Append(t);
            }
        }
        return sb.ToString();
    }
}

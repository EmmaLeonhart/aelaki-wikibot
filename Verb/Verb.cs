using System;
using System.Collections.Generic;
using System.Text;

enum Evid { None, Present, Past, Hearsay, Inferential, 
    PresentPast, PresentHearsay, PresentInferential, 
    PastPresent, PastHearsay, PastInferential, 
    HearsayPresent, HearsayPast, HearsayInferential,
    InferentialPresent, InferentialPast, InferentialHearsay
    }

class Verb
{
    static void Main()
    {
        string root = "kmdr";
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        // 1) your base patterns, with 'v' marking the helper-vowel slot
        var forms = new List<(string name, string pat)>()
        {
            ("Telic Perfect"      , "1-a-2-3-e-4"),
            ("Telic Imperfect"    , "1-a-2-3-o-4"),
            ("Atelic Perfect"     , "1-a-2-v-3-e-4"),
            ("Atelic Imperfect"   , "1-a-2-v-3-o-4"),
            ("Telic Perfect (n)"     , "1-a-2-3-v-3-e-4"),
            ("Habitual Imperfect"    , "1-a-2-3-v-3-o-4"),
            ("Telic Perfect"    , "1-a-2-3-v-2-3-e-4"),
            ("Gnomic Imperfect"      , "1-a-2-3-v-2-3-o-4"),
            ("Atelic Perfect"    , "1-a-2-v-3-v-2-v-3-e-4"),
            ("Atelic Imperfect"     , "1-a-2-v-3-v-2-v-3-o-4"),
            ("Imperative"         , "ala-1-a-2-a-3-4-o")
        };

        // 2) evidential → (helper-vowel, suffix, label)
        var evidMap = new Dictionary<Evid, (string hv, string suffix, string label)>()
        {
            { Evid.None       , ("e",   "",        "Present visual") },
            { Evid.Present    , ("ü",  "-nü",     "Explicit present visual") },
            { Evid.Past       , ("ə",  "-shə",    "Past visual") },
            { Evid.Hearsay    , ("o",  "-ro",     "Past hearsay") },
            { Evid.Inferential, ("u",  "-mu",     "Future inferential") },

            //Present first

            { Evid.PresentPast    , ("ü",  "-nü-shə",     "Yesterday") },
            { Evid.PresentHearsay    , ("ü",  "-nü-ro",     "Reported present") },
            { Evid.PresentInferential    , ("ü",  "-nü-mu",     "Present Inferential") },

            //Past first
            { Evid.PastPresent,        ("ə",  "-shə-nü", "Yesterday") },
            { Evid.PastHearsay,        ("ə",  "-shə-ro", "Mythical times") },
            { Evid.PastInferential,    ("ə",  "-shə-mu", "Past inferential") },

            //Hearsay first
            { Evid.HearsayPresent,     ("o",  "-ro-nü",  "Reported present") },
            { Evid.HearsayPast,        ("o",  "-ro-shə", "Mythical times") },
            { Evid.HearsayInferential, ("o",  "-ro-mu",  "Reported/Promised future") },

            //inferential first

            { Evid.InferentialPresent,            ("u", "-mu-nü", "Present inferential")
            },
            { Evid.InferentialPast,                ("u", "-mu-shə", "Past inferential")
            },
            { Evid.InferentialHearsay,                ("u", "-mu-ro", "Reported/Promised future")
            },

        };

        // 3) generate every form + every evidential (skip evidentials on Imperative)
        foreach (var (name, pat) in forms)
        {
            foreach (var kv in evidMap)
            {
                var ev = kv.Key;
                // no evidential stacking on Imperative
                if (name == "Imperative" && ev != Evid.None)
                    continue;

                // replace 'v' with the helper-vowel
                string withV = pat.Replace("v", kv.Value.hv);

                // build the stem
                string stem = GenerateFromPattern(root, withV);

                // append evidential suffix
                string output = stem + kv.Value.suffix;

                // adjust the output name
                string outName = ev == Evid.None
                    ? name
                    : $"{name} ({kv.Value.label})";

                Console.WriteLine($"{outName.PadRight(20)} → {output}");
            }
        }
    }

    // dash-parser: "1"→root[0], "2"→root[1], etc.
    static string GenerateFromPattern(string root, string pattern)
    {
        var sb = new StringBuilder();
        foreach (var token in pattern.Split('-'))
        {
            if (int.TryParse(token, out int idx) && idx >= 1 && idx <= root.Length)
                sb.Append(root[idx - 1]);
            else
                sb.Append(token);
        }
        return sb.ToString();
    }
}

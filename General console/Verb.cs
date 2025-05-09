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
    static void OldMain()
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

    //public enum Gender { Child, Feminine, Masculine }
    //public enum Plurality { Sing, Plur, Coll, Zero }

    //--------------------------------------------------------------
    //  AddPersonMarkers
    //  -----------------
    //  • core         : the verb stem already built (kamdor, kamdor-ro …)
    //  • subjPers     : 1,2,3,4   (int or enum → th, j, sh, k)
    //  • subjGen      : Child / Fem / Masc
    //  • subjPlur     : false = singular, true = plural → double the prefix
    //  • objPers      : 1,2,3,4
    //  • objGen       : Child / Fem / Masc
    //  • objPlur      : false / true  (zero/collective treated by GenNumber)
    //
    //  Returns: <prefix>(x2?) + core + <suffix>
    //--------------------------------------------------------------
    //-----------------------------------------------------------------
    //  AddPersonMarkers  (Zero now allowed)
    //-----------------------------------------------------------------
    public static string AddPersonMarkers(string core,
                                          int subjPers, General_console.Gender subjGen, General_console.Plurality subjNum,
                                          int objPers, General_console.Gender objGen, General_console.Plurality objNum)
    {
        // (1) person consonants
        string PersCons(int p) => p switch
        {
            1 => "th",
            2 => "j",
            3 => "sh",
            4 => "k",
            _ => ""
        };

        // (2) gender-number vowels
        string GenVowel(General_console.Gender g, General_console.Plurality n) => (g, n) switch
        {
            (General_console.Gender.Child, General_console.Plurality.Singular) => "u",
            (General_console.Gender.Child, General_console.Plurality.Collective) => "i",
            (General_console.Gender.Child, General_console.Plurality.Zero) => "uf",   // child zero
            (General_console.Gender.Feminine, General_console.Plurality.Singular) => "o",
            (General_console.Gender.Feminine, General_console.Plurality.Collective) => "e",
            (General_console.Gender.Feminine, General_console.Plurality.Zero) => "of",
            (General_console.Gender.Masculine, General_console.Plurality.Singular) => "a",
            (General_console.Gender.Masculine, General_console.Plurality.Collective) => "æ",
            (General_console.Gender.Masculine, General_console.Plurality.Zero) => "af",
            _ => ""
        };

        // (3) -------- subject prefix --------
        string sRawV = GenVowel(subjGen, subjNum);
        string sFirstV = sRawV.EndsWith("f") ? sRawV.TrimEnd('f') : sRawV; // remove “f” for zero
        string sPref = PersCons(subjPers) + sFirstV;
        if (subjNum == General_console.Plurality.Plural) sPref += sPref;           // double if plural subject

        // (4) -------- object suffix --------
        string oRawV = GenVowel(objGen, objNum);
        string oFirstV = oRawV.EndsWith("f") ? oRawV.TrimEnd('f') : oRawV;
        string suffix = oFirstV + PersCons(objPers) + oRawV;

        // (5) return full verb
        return sPref + core + suffix;
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


    //-----------------------------------------------------------------
    //  IterateAllVariants
    //  ------------------
    //  Loops over:
    //    • every base‐template in  forms
    //    • every evidential in     evidMap   (skips Imperative combinations)
    //    • every subject person (1-4), gender, number
    //    • every object  person (1-4), gender, number
    //  and prints the fully-inflected verb.
    //
    //  Warning: 4 persons × 3 genders × 4 numbers  ⇒ 48 possibilities
    //            for subject  × 48 for object      ⇒ 2 304
    //            × ~40 stems/evidentials … ≈ 90 000 lines.
    //
    //  Adjust the loops (or add filters) if that’s too large.
    //-----------------------------------------------------------------
    static void IterateAllVariants(
            string root,
            List<(string name, string pat)> forms,
            Dictionary<Evid, (string hv, string suff, string lbl)> evidMap)
    {
        foreach (var (stemName, pat) in forms)
        {
            foreach (var ev in evidMap)
            {
                // skip evidential stacking on Imperative
                if (stemName == "Imperative" && ev.Key != Evid.None) continue;

                // 1) build bare stem (replace v with helper vowel, add suffix)
                string stem = GenerateFromPattern(root, pat.Replace("v", ev.Value.hv))
                              + ev.Value.suff;
                string stemLabel = ev.Key == Evid.None
                     ? stemName
                     : $"{stemName} ({ev.Value.lbl})";

                // 2) loop over subject & object feature sets
                foreach (int sPers in new[] { 1, 2, 3, 4 })
                    foreach (General_console.Gender sGen in Enum.GetValues(typeof(General_console.Gender)))
                        foreach (General_console.Plurality sNum in Enum.GetValues(typeof(General_console.Plurality)))
                            foreach (int oPers in new[] { 1, 2, 3, 4 })
                                foreach (General_console.Gender oGen in Enum.GetValues(typeof(General_console.Gender)))
                                    foreach (General_console.Plurality oNum in Enum.GetValues(typeof(General_console.Plurality)))
                                    {
                                        // subjects probably never use Zero; skip if you wish
                                        if (sNum == General_console.Plurality.Zero) continue;

                                        string full = AddPersonMarkers(stem,
                                                          sPers, sGen, sNum,
                                                          oPers, oGen, oNum);

                                        Console.WriteLine(
                                            $"{stemLabel,-35} | S:{sPers}-{sGen}-{sNum}  O:{oPers}-{oGen}-{oNum}  →  {full}");
                                    }
            }
        }
    }

    /*---------------------------------------------------------------
  Conjugate
  ---------
  Build ONE complete verb:
    • rootSegs     = {"k","m","d","r"}  (multi-char C’s OK)
    • pattern      = "1-a-2-3-e-4"      (one of your base templates)
    • hv / suffix  = helper vowel + evidential suffix
    • subject      = person / gender / plurality
    • object       = person / gender / plurality
----------------------------------------------------------------*/
    static string Conjugate(
            string[] rootSegs,
            string pattern,
            string helperVowel,
            string evidSuffix,
            int subjPers, General_console.Gender subjGen, General_console.Plurality subjNum,
            int objPers, General_console.Gender objGen, General_console.Plurality objNum)
    {
        // 1) root → templatic stem (v → helper-vowel)
        string stem = GenerateFromPattern(rootSegs, pattern.Replace("v", helperVowel));

        // 2) add evidential suffix (may be "")
        stem += evidSuffix;

        // 3) add subject / object agreement
        return AddPersonMarkers(stem,
                subjPers, subjGen, subjNum,
                objPers, objGen, objNum);
    }

    /* ----- overload for segmented root ----- */
    static string GenerateFromPattern(string[] segs, string pattern)
    {
        var sb = new StringBuilder();
        foreach (var token in pattern.Split('-'))
        {
            if (int.TryParse(token, out int idx) &&
                idx >= 1 && idx <= segs.Length)
                sb.Append(segs[idx - 1]);
            else
                sb.Append(token);
        }
        return sb.ToString();
    }

    /*---------------------------------------------------------------
      AllConjugations
      ---------------
      List every conjugation for the given subject/object settings
    ----------------------------------------------------------------*/
    internal static void AllConjugations(
            string[] rootSegs,
            General_console.Gender sg, General_console.Plurality sp, General_console.Person sper,
            General_console.Plurality op, General_console.Person oper)
    {
        var forms = BuildForms();      // base templates (helper below)
        var evidMap = BuildEvidMap();    // evidential bundles (already in file)

        Console.WriteLine($"\n=== Conjugations for root {string.Join("", rootSegs)} ===");
        Console.WriteLine($"   Subject = {sper}-{sg}-{sp}");
        Console.WriteLine($"   Object  = {oper}-Child-{op}\n");

        foreach (var (stemName, pat) in forms)
        {
            foreach (var ev in evidMap)
            {
                if (stemName == "Imperative" && ev.Key != Evid.None) continue; // no stack

                string full = Conjugate(
                    rootSegs, pat, ev.Value.hv, ev.Value.suffix,
                    (int)sper, sg, sp,
                    (int)oper, General_console.Gender.Child, op   // object gender child (change if needed)
                );

                string label = ev.Key == Evid.None
                    ? stemName
                    : $"{stemName} ({ev.Value.label})";

                Console.WriteLine($"{label.PadRight(35)} → {full}");
            }
        }
    }

    internal static void Conjugate(
            string[] rootSegs,
            General_console.Gender sg, General_console.Plurality sp, General_console.Person sper,
            General_console.Plurality op, General_console.Person oper)
    {

        //do one that conjugates Telic Imperfect with no evidentiality

    }

    /*---------------- helper: base-template list ------------------*/
    static List<(string name, string pat)> BuildForms() => new()
{
    ("Telic Perfect"     , "1-a-2-3-e-4"),
    ("Telic Imperfect"   , "1-a-2-3-o-4"),
    ("Atelic Perfect"    , "1-a-2-v-3-e-4"),
    ("Atelic Imperfect"  , "1-a-2-v-3-o-4"),
    ("Telic Perfect (n)" , "1-a-2-3-v-3-e-4"),
    ("Habitual Imperf."  , "1-a-2-3-v-3-o-4"),
    ("Telic Perfect **"  , "1-a-2-3-v-2-3-e-4"),
    ("Gnomic Imperfect"  , "1-a-2-3-v-2-3-o-4"),
    ("Atelic Perfect **" , "1-a-2-v-3-v-2-v-3-e-4"),
    ("Atelic Imperf. **" , "1-a-2-v-3-v-2-v-3-o-4"),
    ("Imperative"        , "ala-1-a-2-a-3-4-o")
};

    /* ----- tiny helper to keep the evidential map out of the way ----- */
    static Dictionary<Evid, (string hv, string suffix, string label)> BuildEvidMap()
    {
        return new()
    {
        { Evid.None,               ("e",  "",          "Present visual") },
        { Evid.Present,            ("ü", "-nü",        "Explicit present") },
        { Evid.Past,               ("ə", "-shə",       "Past visual") },
        { Evid.Hearsay,            ("o", "-ro",        "Past hearsay") },
        { Evid.Inferential,        ("u", "-mu",        "Future inferential") },
        { Evid.PresentPast,        ("ü","-nü-shə","Yesterday") },
        { Evid.PresentHearsay,     ("ü","-nü-ro", "Reported present") },
        { Evid.PresentInferential, ("ü","-nü-mu", "Present inferential") },
        { Evid.PastPresent,        ("ə","-shə-nü","Yesterday") },
        { Evid.PastHearsay,        ("ə","-shə-ro","Mythical past") },
        { Evid.PastInferential,    ("ə","-shə-mu","Past inferential") },
        { Evid.HearsayPresent,     ("o","-ro-nü", "Reported present") },
        { Evid.HearsayPast,        ("o","-ro-shə","Mythical past") },
        { Evid.HearsayInferential, ("o","-ro-mu", "Promised future") },
        { Evid.InferentialPresent, ("u","-mu-nü", "Present inferential") },
        { Evid.InferentialPast,    ("u","-mu-shə","Past inferential") },
        { Evid.InferentialHearsay, ("u","-mu-ro", "Promised future") },
    };

    }
}

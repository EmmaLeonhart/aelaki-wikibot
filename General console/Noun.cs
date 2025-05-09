using System;
using System.Collections.Generic;
using static System.Console;

namespace AelakiNounGen
{
    //enum Gender { Child, Feminine, Masculine }
    //enum Number { Singular, Plural, Collective, Zero }
    //enum Person { First, Second, Third, Fourth }

    class Noun
    {
        // Person → noun-suffix map
        static readonly Dictionary<General_console.Person, string> PersonSuffix = new()
        {
            { General_console.Person.First,  "th" },
            { General_console.Person.Second, "j" },
            { General_console.Person.Third,  "sh" },
            { General_console.Person.Fourth, ""   }  // default
        };

        // Person → consonantal marker for head-marking
        static readonly Dictionary<General_console.Person, string> PersonCons = new()
        {
            { General_console.Person.First,  "th" },
            { General_console.Person.Second, "j" },
            { General_console.Person.Third,  "sh" },
            { General_console.Person.Fourth, "k"  }
        };

        // Gender → (middle vowel, end vowel)
        static (char mid, char end) VowelSlots(General_console.Gender g) => g switch
        {
            General_console.Gender.Child => ('u', 'u'),
            General_console.Gender.Feminine => ('o', 'o'),
            General_console.Gender.Masculine => ('a', 'a'),
            _ => throw new ArgumentOutOfRangeException()
        };

        // Build the noun stem (performer) for Sing/Plur/Coll
        static string BuildStemTetra(string[] root, General_console.Gender g, General_console.Plurality n)
        {
            // root: four consonants, each may be multiple letters
            string C1 = root[0], C2 = root[1], C3 = root[2], C4 = root[3];
            var (vm, ve) = VowelSlots(g);

            // Singular template: C1-a-C2-u-C3-vm-C4-ve
            string singular = $"{C1}a{C2}u{C3}{vm}{C4}{ve}";

            if (n == General_console.Plurality.Singular)
                return singular;

            // Plural: duplicate "C2u"
            string plural = $"{C1}a{C2}u{C2}u{C3}{vm}{C4}{ve}";
            if (n == General_console.Plurality.Plural)
                return plural;
            else if (n == General_console.Plurality.Zero)
                return singular
                    .Replace("u", "uf")
                    .Replace("o", "of")
                    .Replace("ə", "əf");

            // Collective: from plural, shift u→i, o→e, ə→æ
            return singular
                .Replace("u", "i")
                .Replace("o", "e")
                .Replace("ə", "æ");
        }

        // Append person suffix for non-genitive paradigms
        static string BuildFormTetra(string[] root, General_console.Gender g, General_console.Plurality n, General_console.Person p)
            => (BuildStemTetra(root, g, n) + PersonSuffix[p]).ToLower();

        // Build the **possessor** (dependent) NP
        // prefix "kae-", then the 4th-person noun form, then GV+"ng"/"n"
        static string BuildPossessor(string[] root, General_console.Gender g, General_console.Plurality n, bool inalienable)
        {
            // get the default (4th person) noun form
            string baseNoun = BuildFormTetra(root, g, n, General_console.Person.Fourth);
            char GV = VowelSlots(g).end;
            string suff = inalienable ? $"ng" : $"n";
            return $"{baseNoun}{suff}";
        }

        // Build the **possessed** (head) NP
        // inalienable: C1 + GV + PC + restOfStem
        // alienable:    GV + PC + restOfStem
        static string BuildPossessed(string[] root, General_console.Gender g, General_console.Plurality n, General_console.Person possessor, bool inalienable)
        {
            string stem = BuildStemTetra(root, g, n);
            string C1 = stem.Substring(0, root[0].Length);      // first consonant chunk
            char GV = VowelSlots(g).end;
            string PC = PersonCons[possessor];
            string rest = stem.Substring(root[0].Length);       // drop the first consonant chunk

            if (inalienable)
                return $"{C1}{GV}{PC}{rest}";
            else
                return $"{GV}{PC}{C1}{rest}";
        }

        // Small IPA helper
        static string ToIPA(string w)
            => "/" + w
                .Replace("sh", "ʃ")
                .Replace("j", "dʒ")
                .Replace("th", "θ")
            + "/";

        static void OldMain()
        {
            // example root: K–M–D–R
            // could also be new[]{"t","l","k","p"} etc.
            string[] root = new[] { "k", "m", "d", "r" };

            var genders = new[] { General_console.Gender.Child, General_console.Gender.Feminine, General_console.Gender.Masculine };
            var numbers = new[] { General_console.Plurality.Singular, General_console.Plurality.Plural, General_console.Plurality.Collective, General_console.Plurality.Zero };
            var persons = new[] { General_console.Person.First, General_console.Person.Second, General_console.Person.Third, General_console.Person.Fourth };

            // 1) Non-genitive paradigms
            WriteLine("=== Non-Genitive Paradigms ===\n");
            foreach (var g in genders)
            {
                WriteLine($"-- {g} --");
                foreach (var n in numbers)
                {
                    foreach (var p in persons)
                    {
                        string form = BuildFormTetra(root, g, n, p);
                        WriteLine($"{n,-10} {p,-6} {form,-12} {ToIPA(form)}");
                    }
                }
                WriteLine();
            }

            // 2) Genitive paradigms
            WriteLine("=== Genitive Paradigms ===\n");
            foreach (var g in genders)
            {
                WriteLine($"-- {g} --");
                foreach (var n in numbers)
                {
                    WriteLine($"\n * {n} *");
                    foreach (var p in persons)
                    {
                        var possIn = BuildPossessor(root, g, n, inalienable: true);
                        var possAl = BuildPossessor(root, g, n, inalienable: false);
                        var headIn = BuildPossessed(root, g, n, p, inalienable: true);
                        var headAl = BuildPossessed(root, g, n, p, inalienable: false);

                        WriteLine($" Possessor (inalien.): {possIn,-20} {ToIPA(possIn)}");
                        WriteLine($" Possessor (alienable):{possAl,-20} {ToIPA(possAl)}");
                        WriteLine($" Head     (inalien.): {headIn,-20} {ToIPA(headIn)}");
                        WriteLine($" Head     (alienable):{headAl,-20} {ToIPA(headAl)}");
                        WriteLine();
                    }
                }
                WriteLine();
            }
        }

        internal static string BuildStem(General_console.Gender gender, General_console.Plurality plurality, string root)
        {

            throw new NotImplementedException();
        }

        internal static string BuildStem(General_console.Gender gender, General_console.Plurality plurality, General_console.Person person, string c1, string c2, string c3, string c4)
        {
            string[] ints;
            if (c4 == "") {
                ints = new string[] { c1, c2, c3 };
                return BuildStemTri(ints, gender, plurality);
            }
            else 
            {
                ints = new string[] { c1, c2, c3, c4 };
                return BuildFormTetra(ints, gender, plurality, person);
            }
            throw new NotImplementedException();
        }

        private static string BuildStemTri(string[] ints, General_console.Gender gender, General_console.Plurality plurality)
        {
            throw new NotImplementedException();
        }
    }
}

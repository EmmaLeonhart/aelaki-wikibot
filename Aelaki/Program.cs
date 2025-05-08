using System;
using System.Collections.Generic;
using static System.Console;

namespace AelakiNounGen
{
    enum Gender { Child, Feminine, Masculine }
    enum Number { Singular, Plural, Collective, Zero }
    enum Person { First, Second, Third, Fourth }

    class Program
    {
        // Person → noun-suffix map
        static readonly Dictionary<Person, string> PersonSuffix = new()
        {
            { Person.First,  "th" },
            { Person.Second, "tl" },
            { Person.Third,  "sh" },
            { Person.Fourth, ""   }  // default
        };

        // Person → consonantal marker for head-marking
        static readonly Dictionary<Person, string> PersonCons = new()
        {
            { Person.First,  "th" },
            { Person.Second, "tl" },
            { Person.Third,  "sh" },
            { Person.Fourth, "k"  }
        };

        // Gender → (middle vowel, end vowel)
        static (char mid, char end) VowelSlots(Gender g) => g switch
        {
            Gender.Child => ('u', 'u'),
            Gender.Feminine => ('o', 'o'),
            Gender.Masculine => ('a', 'a'),
            _ => throw new ArgumentOutOfRangeException()
        };

        // Build the noun stem (performer) for Sing/Plur/Coll
        static string BuildStem(string[] root, Gender g, Number n)
        {
            // root: four consonants, each may be multiple letters
            string C1 = root[0], C2 = root[1], C3 = root[2], C4 = root[3];
            var (vm, ve) = VowelSlots(g);

            // Singular template: C1-a-C2-u-C3-vm-C4-ve
            string singular = $"{C1}a{C2}u{C3}{vm}{C4}{ve}";

            if (n == Number.Singular)
                return singular;

            // Plural: duplicate "C2u"
            string plural = $"{C1}a{C2}u{C2}u{C3}{vm}{C4}{ve}";
            if (n == Number.Plural)
                return plural;
            else if (n == Number.Zero)
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
        static string BuildForm(string[] root, Gender g, Number n, Person p)
            => (BuildStem(root, g, n) + PersonSuffix[p]).ToLower();

        // Build the **possessor** (dependent) NP
        // prefix "kae-", then the 4th-person noun form, then GV+"ng"/"n"
        static string BuildPossessor(string[] root, Gender g, Number n, bool inalienable)
        {
            // get the default (4th person) noun form
            string baseNoun = BuildForm(root, g, n, Person.Fourth);
            char GV = VowelSlots(g).end;
            string suff = inalienable ? $"ng" : $"n";
            return $"{baseNoun}{suff}";
        }

        // Build the **possessed** (head) NP
        // inalienable: C1 + GV + PC + restOfStem
        // alienable:    GV + PC + restOfStem
        static string BuildPossessed(string[] root, Gender g, Number n, Person possessor, bool inalienable)
        {
            string stem = BuildStem(root, g, n);
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
                .Replace("tl", "tɬ")
                .Replace("th", "θ")
            + "/";

        static void Main()
        {
            // example root: K–M–D–R
            // could also be new[]{"t","l","k","p"} etc.
            string[] root = new[] { "k", "m", "d", "r" };

            var genders = new[] { Gender.Child, Gender.Feminine, Gender.Masculine };
            var numbers = new[] { Number.Singular, Number.Plural, Number.Collective };
            var persons = new[] { Person.First, Person.Second, Person.Third, Person.Fourth };

            // 1) Non-genitive paradigms
            WriteLine("=== Non-Genitive Paradigms ===\n");
            foreach (var g in genders)
            {
                WriteLine($"-- {g} --");
                foreach (var n in numbers)
                {
                    foreach (var p in persons)
                    {
                        string form = BuildForm(root, g, n, p);
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
    }
}

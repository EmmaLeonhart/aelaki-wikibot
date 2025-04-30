using System;
using System.Collections.Generic;
using System.Text;
using static System.Console;

namespace Aelaki
{
    // ENUMS --------------------------------------------------------------
    enum Gender { Feminine, Child, Masculine }
    enum Number { Singular, Plural, Collective }
    enum Person { First, Second, Third, Fourth }

    // MAIN PROGRAM -------------------------------------------------------
    class Program
    {
        static void Main()
        {
            string root = "bsl";          // ► put any 3-consonant root here
            foreach (var g in Enum.GetValues(typeof(Gender)))
                foreach (var n in Enum.GetValues(typeof(Number)))
                    foreach (var p in Enum.GetValues(typeof(Person)))
                    {
                        string form = NounGen(root, (Gender)g, (Number)n, (Person)p);
                        string ipa = ToIPA(form);
                        WriteLine($"{g,-10} {n,-10} {p,-6}  {form,-12} {ipa}");
                    }
        }

        // CORE GENERATOR -------------------------------------------------
        static string NounGen(string root, Gender g, Number n, Person p)
        {
            if (root.Length != 3) throw new ArgumentException("Root must be 3 consonants");

            char C1 = root[0], C2 = root[1], C3 = root[2];

            // --- base stem by gender & number ---
            string stem = (g, n) switch
            {
                (Gender.Feminine, Number.Singular) => $"{C1}a{C2}o{C3}",
                (Gender.Feminine, Number.Plural) => $"{C1}a{C2}a{C1}o{C3}",
                (Gender.Feminine, Number.Collective) => $"{C1}a{C2}e{C3}",

                (Gender.Child, Number.Singular) => $"{C1}a{C2}u{C3}",
                (Gender.Child, Number.Plural) => $"{C1}a{C2}a{C1}u{C3}",
                (Gender.Child, Number.Collective) => $"{C1}a{C2}i{C3}",

                (Gender.Masculine, Number.Singular) => $"{C1}a{C2}a{C3}",
                (Gender.Masculine, Number.Plural) => $"{C1}a{C2}a{C1}a{C3}",
                (Gender.Masculine, Number.Collective) => $"{C1}a{C2}æ{C3}",

                _ => throw new InvalidOperationException("Unhandled pattern")
            };

            // --- person suffixes (4th = no suffix) ---
            string suffix = p switch
            {
                Person.Fourth => "",
                Person.Third => "sh",
                Person.Second => "tl",
                Person.First => "th",
                _ => ""
            };

            return (stem + suffix).ToLower();
        }

        // SIMPLE IPA CONVERTER ------------------------------------------
        static string ToIPA(string s)
        {
            var ipa = s
                .Replace("sh", "ʃ")
                .Replace("tl", "tɬ")
                .Replace("th", "θ")
                .Replace("æ", "æ");
            return "/" + ipa + "/";
        }
    }
}

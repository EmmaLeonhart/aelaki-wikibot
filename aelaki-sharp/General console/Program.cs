using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using System.Text;
using static System.Runtime.InteropServices.JavaScript.JSType;

namespace General_console
{
    /* -----------------------------------------------------------
     *  0.  Your AelakiNumber (unchanged – only the print helper)
     * ----------------------------------------------------------- */
    //class AelakiNumber
    //{
    //    public int Value;
    //    public AelakiNumber(int c4) => Value = c4;

    //    public void PrintAllNumbersUpTo60()
    //    {
    //        for (int i = 1; i <= 60; i++)
    //            Console.WriteLine($"{i} → {i}");
    //    }
    //}

    /* -----------------------------------------------------------
     *  1.  Core feature enums
     * ----------------------------------------------------------- */
    public enum Person { First = 1, Second, Third, Fourth }
    public enum Gender { Child, Feminine, Masculine }
    public enum Plurality { Singular, Plural, Collective, Zero }
    //public enum Evid { None, Present, Past, Hearsay, Inferential }
    public enum VerbType { Transitive, Active, Stative }

    /* -----------------------------------------------------------
     *  2.  Very small noun generator (just enough for demo)
     * ----------------------------------------------------------- */
    public static class NounGenerator
    {
        // C1-a-C2-(Gv1)-C3-(Gv2)  (only singular shown)
        public static string Build(string root, Gender g, Plurality n, Person p)
        {
            var C = root.ToCharArray();
            string v1 = g switch { Gender.Child => "u", Gender.Feminine => "o", _ => "a" };
            string v2 = v1;                                           // about same rule
            string baseForm = $"{C[0]}a{C[1]}{v1}{C[2]}{v2}";

            // plural / collective / zero normally adjust but kept simple here
            // add person suffix
            string psuf = p switch { Person.First => "th", Person.Second => "j", Person.Third => "sh", _ => "" };
            return baseForm + psuf;
        }
    }

    /* -----------------------------------------------------------
     *  3.  TransitiveVerb generator (single template for demo)
     *      – Telic Imperfect stem = 1-a-2-3-o-4
     * ----------------------------------------------------------- */
    public static class VerbGenerator
    {
        public static string Build(string root, Evid evid,
                                   Person sPers, Gender sGen, Plurality sNum,
                                   Person oPers, Gender oGen, Plurality oNum)
        {
            var C = root.ToCharArray();
            string stem = $"{C[0]}a{C[1]}{C[2]}o{C[3]}";   // kamdor for k-m-d-r

            // evid suffix (only Past visual for brevity)
            string evidSuf = evid == Evid.Past ? "-shə" : "";

            // person-gender affixes (simple)
            string Pref(Gender g) => g switch { Gender.Child => "u", Gender.Feminine => "o", _ => "a" };
            string Cons(Person p) => p switch { Person.First => "th", Person.Second => "j", Person.Third => "sh", _ => "k" };

            string subj = Cons(sPers) + Pref(sGen);        // th + a  => tha
            string objV = Pref(oGen);
            string objSuf = objV + Cons(oPers) + objV;     // o + sh + o  => osho

            return subj + stem + evidSuf + objSuf;
        }
    }
}
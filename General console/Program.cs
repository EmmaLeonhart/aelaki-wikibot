using System;
using System.Collections.Generic;
using System.Text;

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
    public enum Number { Singular, Plural, Collective, Zero }
    public enum Evid { None, Present, Past, Hearsay, Inferential }

    /* -----------------------------------------------------------
     *  2.  Very small noun generator (just enough for demo)
     * ----------------------------------------------------------- */
    public static class NounGenerator
    {
        // C1-a-C2-(Gv1)-C3-(Gv2)  (only singular shown)
        public static string Build(string root, Gender g, Number n, Person p)
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
     *  3.  Verb generator (single template for demo)
     *      – Telic Imperfect stem = 1-a-2-3-o-4
     * ----------------------------------------------------------- */
    public static class VerbGenerator
    {
        public static string Build(string root, Evid evid,
                                   Person sPers, Gender sGen, Number sNum,
                                   Person oPers, Gender oGen, Number oNum)
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

    /* -----------------------------------------------------------
     *  4.  Clause objects
     * ----------------------------------------------------------- */
    class NounPhrase
    {
        public string Root;
        public Person Person;
        public Gender Gender;
        public Number Number;
        public bool Dropped;
        private string c1;
        private string c2;
        private string c3;
        private string c4;

        public NounPhrase(Gender child, Number singular, Person first) //dropped constructor
        {
            this.Person = first;
            this.Gender = child;
            this.Number = singular; 
            this.Dropped = true;
        }

        public NounPhrase(Gender child, Number singular, Person first, string v1, string v2, string v3) : this(child, singular, first) //triconsonantal constructor
        {
            this.c1 = v1;
            this.c2 = v2;
            this.c3 = v3;
            this.Dropped = false;
        }

        public NounPhrase(Gender child, Number singular, Person first, string v1, string v2, string v3, string v) : this(child, singular, first, v1, v2, v3) //tetraconsonantal constructor
        {
            this.c4 = v;
            this.Dropped = false;
        }

        public string Surface => Dropped ? "" :
             NounGenerator.Build(Root, Gender, Number, Person);
    }

    class VerbPhrase
    {
        public string Root;
        public Evid Evid;
        public Person SubjPerson;
        public Gender SubjGender;
        public Number SubjNumber;
        public Person ObjPerson;
        public Gender ObjGender;
        public Number ObjNumber;

        public string Surface => VerbGenerator.Build(
                Root, Evid,
                SubjPerson, SubjGender, SubjNumber,
                ObjPerson, ObjGender, ObjNumber);
    }

    class Clause
    {
        public NounPhrase Subject;
        public NounPhrase Object;
        public VerbPhrase Verb;

        public override string ToString()
            => $"{Subject.Surface}{Object.Surface}{Verb.Surface}";
    }

    /* -----------------------------------------------------------
     *  5.  Demonstration
     * ----------------------------------------------------------- */
    class Program
    {
        static void Main()
        {
            var n = new AelakiNumber(1);
            n.PrintAllNumbersUpTo60();
            Console.WriteLine("\nNow we are trying to make sentences\n");

            /* “The exalted (masc sg) ate the tree (fem sg) yesterday.” */

            // subject NP (dropped – info lives on verb)
            //var subj = new NounPhrase { Dropped = true };

            var subj = new NounPhrase(Gender.Child, Number.Singular, Person.First);

            var obj = new NounPhrase(Gender.Child, Number.Singular, Person.First, "b", "s", "l");

            var ind = new NounPhrase(Gender.Child, Number.Singular, Person.First, "k", "m", "d", "r");

            // object NP  “tree”  (root b-s-l, fem sg 4th person)
            //var obj = new NounPhrase
            //{
            //    Root = "bsl",
            //    Gender = Gender.Feminine,
            //    Number = Number.Singular,
            //    Person = Person.Fourth,
            //    Dropped = false
            //};

            // verb  kamdor-shə + person markers
            var vp = new VerbPhrase
            {
                Root = "kmdr",
                Evid = Evid.Past,
                SubjPerson = Person.Third,
                SubjGender = Gender.Masculine,
                SubjNumber = Number.Singular,
                ObjPerson = Person.Fourth,
                ObjGender = Gender.Feminine,
                ObjNumber = Number.Singular
            };

            var clause = new Clause { Subject = subj, Object = obj, Verb = vp };

            Console.WriteLine("Aelaki sentence:");
            Console.WriteLine(clause);           // prints fully inflected form
        }
    }
}

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
    public enum Evid { None, Present, Past, Hearsay, Inferential }
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
     *  3.  Verb generator (single template for demo)
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

    /* -----------------------------------------------------------
     *  4.  Clause objects
     * ----------------------------------------------------------- */
    class NounPhrase
    {
        public string Root;
        public Person Person;
        public Gender Gender;
        public Plurality Plurality;
        public bool Dropped;
        private string c1;
        private string c2;
        private string c3;
        private string c4;
        public List<StativeAdjective> FrontAdjectives { get; private set; }

        public List<StativeAdjective> BackAdjectives { get; private set; }

        public AelakiNumber Number { get; private set; }

        public override string ToString()
        {
            string s = "";
            if (FrontAdjectives != null) {
                foreach (StativeAdjective a in FrontAdjectives)
                {
                    Console.WriteLine("Testing adjective");
                    Console.WriteLine(a.realize(this));
                    s += a.realize(this);
                    s += " ";
                }
            }
            Console.WriteLine("What we have so far: ");
            Console.WriteLine(s);
            s += NounPronounciation();
            Console.WriteLine("What we have so far: ");
            Console.WriteLine(s);
            return s;
            throw new NotImplementedException();
            return base.ToString();
        }

        private string NounPronounciation()
        {
            if (Dropped == true)
            {
                return "";
            }
            else if (Posessor != null)
            {
                return AelakiNounGen.Noun.BuildStemPossesed(this.Posessor, this.Gender, this.Plurality, this.Person, c1, c2, c3, c4);
            }
            else
            {
                return AelakiNounGen.Noun.BuildStem(this.Gender, this.Plurality, this.Person, c1, c2, c3, c4);
            }
            throw new NotImplementedException();
        }

        public NounPhrase(Gender child, Plurality singular, Person first) //dropped constructor
        {
            this.Person = first;
            this.Gender = child;
            this.Plurality = singular;
            this.Dropped = true;
        }

        public NounPhrase(Gender child, Plurality singular, Person first, string v1, string v2, string v3) : this(child, singular, first) //triconsonantal constructor
        {
            this.c1 = v1;
            this.c2 = v2;
            this.c3 = v3;
            this.Dropped = false;
        }

        public NounPhrase(Gender child, Plurality singular, Person first, string v1, string v2, string v3, string v) : this(child, singular, first, v1, v2, v3) //tetraconsonantal constructor
        {
            this.c4 = v;
            this.Dropped = false;
        }

        public string Surface => Dropped ? "" :
             NounGenerator.Build(Root, Gender, Plurality, Person);

        public Posessor Posessor { get; private set; }

        internal void AddAdjective(StativeAdjective adjective)
        {
            bool front = true;
            this.AddAdjective(adjective, front);
        }

        private void AddAdjective(StativeAdjective adjective, bool front)
        {
            adjective.noun = this;
            if (front)
            {
                if (this.FrontAdjectives == null)
                {
                    this.FrontAdjectives = new List<StativeAdjective>();
                }
                this.FrontAdjectives.Add(adjective);
            }
            else
            {
                if (this.BackAdjectives == null)
                {
                    this.BackAdjectives = new List<StativeAdjective>();
                }
                this.BackAdjectives.Add(adjective);
            }
        }

        internal void AddNumber(int number)
        {
            AelakiNumber aelakiNumber = new AelakiNumber(number);
            AddNumber(aelakiNumber);
        }

        internal void AddNumber(AelakiNumber number)
        {

            this.Number = number;
            number.Noun = this;
            if (this.Plurality == Plurality.Singular)
            {
                if (this.Number > 1)
                {
                    this.Plurality = Plurality.Plural;
                }
            }
            if (this.FrontAdjectives == null)
            {
                this.FrontAdjectives = new List<StativeAdjective>();
            }
            this.FrontAdjectives.Add(StativeAdjective.AdaptNumber(number));
        }

        internal void AddRoot(string v1, string v2, string v3, string v4)
        {
            c1 = v1;
            c2 = v2;
            c3 = v3;
            c4 = v4;
            this.Dropped = false;
        }

        internal void AddPosessor(string v1, string v2, string v3, Gender feminine, Person fourth, Plurality singular, bool alienable)
        {
            this.Posessor = new Posessor(v1, v2, v3, feminine, fourth, singular, alienable);
            throw new NotImplementedException();
        }

        internal void AddPosessor(string v1, string v2, string v3, string v4, Gender feminine, Person fourth, Plurality singular, bool inalienable)
        {
            this.Posessor = new Posessor(v1, v2, v3, v4, feminine, fourth, singular, inalienable);
            //throw new NotImplementedException();

            if (this.FrontAdjectives == null)
            {
                this.FrontAdjectives = new List<StativeAdjective>();
            }
            this.FrontAdjectives.Add(this.Posessor);
        }
    }

    class VerbPhrase
    {
        public string[] Root;
        private bool active;
        public Evid Evid;
        public Person SubjPerson;
        public Gender SubjGender;
        public Plurality SubjNumber;
        public Person ObjPerson;
        public Gender ObjGender;
        public Plurality ObjNumber;
        private string c1;
        private string c2;
        private string c3;
        private string c4;

        public string ToString(NounPhrase subject, NounPhrase @object)
        {
            string s = "";
            if (this.AdverbList != null)
            {
                foreach (Adverb a in this.AdverbList)
                {
                    s += a.realize(this);
                    s += " ";
                }
            }
            s += this.realize(subject, @object);
            //throw new NotImplementedException();
            return s;
            return base.ToString();
        }

        private string realize(NounPhrase subject, NounPhrase @object)
        {
            Gender sg = subject.Gender;
            Plurality sp = subject.Plurality;
            Person sper = subject.Person;
            Gender og = @object.Gender;
            Plurality op = @object.Plurality;
            Person oper = @object.Person;
            return Verb.Conjugate(Root, sg, sp, sper, og, op, oper);
            //throw new NotImplementedException();
        }

        private string realize()
        {
            throw new NotImplementedException();
        }

        public VerbPhrase(string v1, string v2, string v3, string v4)
        {
            this.Root = new string[] { v1, v2, v3, v4 };
            this.VerbType = VerbType.Transitive;
        }

        public VerbPhrase(bool active, string v1, string v2, string v3)
        {
            this.Root = new string[] { v1, v2, v3 };
            if (active) {
                this.VerbType = VerbType.Active;
            }
            else
            {
                this.VerbType = VerbType.Stative;
            }
        }

        public object Surface { get; private set; }
        public VerbType VerbType { get; private set; }
        public List<Adverb> AdverbList { get; private set; }

        //    public string Surface => VerbGenerator.Build(
        //            Root, Evid,
        //            SubjPerson, SubjGender, SubjNumber,
        //            ObjPerson, ObjGender, ObjNumber);
        //}

        class Clause
        {
            public NounPhrase Subject;
            public NounPhrase Object;
            public VerbPhrase Verb;

            public override string ToString(){
                string s = "";
                s += Subject.ToString();
                s += " ";
                s += Verb.ToString(Subject, Object);
                s += Object.ToString();
                return s;
            }
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

                /* “The group of 60 children worshippers worshipped a singular goddess.” */

                // subject NP (dropped – info lives on verb)
                //var subj = new NounPhrase { Dropped = true };

                var subj = new NounPhrase(Gender.Child, Plurality.Collective, Person.Fourth);

                var obj = new NounPhrase(Gender.Feminine, Plurality.Singular, Person.Fourth);

                var ind = new NounPhrase(Gender.Child, Plurality.Singular, Person.First, "k", "m", "d", "r");

                

                subj.AddNumber(60);

                subj.AddRoot("k", "m", "d", "r");

                bool alienable = true;

                subj.AddPosessor("y", "z", "g", "t", Gender.Feminine, Person.Fourth, Plurality.Singular, alienable);


                //subj.AddAdjective(new StativeAdjective("b", "s", "l"));

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
                //var vp = new VerbPhrase
                //{
                //    Root = "kmdr",
                //    Evid = Evid.Past,
                //    SubjPerson = Person.Third,
                //    SubjGender = Gender.Masculine,
                //    SubjNumber = Plurality.Singular,
                //    ObjPerson = Person.Fourth,
                //    ObjGender = Gender.Feminine,
                //    ObjNumber = Plurality.Singular
                //};

                var Verb = new VerbPhrase("k", "m", "d", "r");

                //Verb.AddAdverb(new Adverb("k", "m", "d", "r"));


                var clause = new Clause { Subject = subj, Object = obj, Verb = Verb };

                Console.WriteLine("Aelaki sentence:");
                Console.WriteLine(subj.ToString());
                //subj.Dropped = true;
                Console.WriteLine(clause);           // prints fully inflected form
            }
        }

        private void AddAdverb(Adverb adverb)
        {
            if (this.AdverbList == null)
            {
                this.AdverbList = new List<Adverb>();
            }
            this.AdverbList.Add(adverb);
        }
    }
}
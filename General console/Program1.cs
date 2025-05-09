
namespace General_console
{
    partial class VerbPhrase
    {
        /* -----------------------------------------------------------
         *  5.  Demonstration
         * ----------------------------------------------------------- */
        class Program
        {
            static void Main()
            {
                var n = new AelakiNumber(1);
                n.PrintAllNumbersUpTo60();
                AelakiNumber.allfractions();
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




                subj.AddAdjective(new StativeAdjective("b", "s", "l"));

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

                Verb.AddAdverb(30);

                //TransitiveVerb.AddAdverb(new Adverb("k", "m", "d", "r"));


                var clause = new Clause { Subject = subj, Object = obj, Verb = Verb };

                Console.WriteLine("Aelaki sentence:");
                Console.WriteLine(subj.ToString());
                //subj.Dropped = true;
                Console.WriteLine(clause);           // prints fully inflected form
            }
        }

        private void AddAdverb(int v)
        {
            throw new NotImplementedException();
        }
    }
}
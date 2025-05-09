
using System.Runtime.CompilerServices;

namespace General_console
{
    public interface Adjective
    {
        // A read-only property
        string Type { get; }

    }

    public enum Evid
    {
        None, Present, Past, Hearsay, Inferential
    }

    internal class StativeAdjective : Adjective
    {


        Dictionary<Evid, (string hv, string suffix, string label)> evidMap = new Dictionary<Evid, (string hv, string suffix, string label)>()
        {
            { Evid.None       , ("e",   "",        "Neutral") },
            { Evid.Present    , ("ü",  "-nü",     "Present as opposed to when it was happening") },
            { Evid.Past       , ("ə",  "-shə",    "Past") },
            { Evid.Hearsay    , ("o",  "-ro",     "testimony") },
            { Evid.Inferential, ("u",  "-mu",     "inferential") }

        };

        string PersCons(Person p) => p switch
        {
            Person.First => "th",
            Person.Second => "j",
            Person.Third => "sh",
            Person.Fourth => "k"
        };


        internal NounPhrase noun;
        private string[] root;

        public StativeAdjective(string c1, string c2, string c3) 
        {
            string[] root = { c1, c2, c3 };
            this.root = root;
        }

        public string Type => "Stative Adjective derived from TransitiveVerb";

        internal static NumberAdjective AdaptNumber(AelakiNumber number)
        {
            return new NumberAdjective(number);
        }

        public static string genderVowel(Gender g, Plurality p)
        {
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
            return GenVowel(g, p);
        }

        internal virtual string realize(NounPhrase nounPhrase)
        {
            return realize(nounPhrase, Evid.None);
            throw new NotImplementedException();
        }
        internal virtual string realize(NounPhrase nounPhrase, Evid e)
        {
            string s = this.root[0];
            s += "o";
            s += this.root[1];
            s += "a";
            s += this.root[2];
            //e = Evid.Inferential;
            if (e == Evid.None)
            {
                s += genderVowel(nounPhrase.Gender, nounPhrase.Plurality);
            }
            else
            {
                s += evidMap[e].suffix;
                Console.WriteLine(s);
                var (hv, suffix, label) = evidMap[e];
            }
            s += PersCons(nounPhrase.Person) + genderVowel(nounPhrase.Gender, nounPhrase.Plurality);
            Console.WriteLine(s);
            return s;
            throw new NotImplementedException();
        }
    }

    internal class NumberAdjective : StativeAdjective
    {
        private AelakiNumber number;
        private static readonly string c1 = "c1";
        private static readonly string c2 = "c2";
        private static readonly string c3 = "c3";

        public NumberAdjective(AelakiNumber number)
            : base(c1, c2, c3)
        {
            this.number = number;
        }

        internal override string realize(NounPhrase nounPhrase)
        {
            return AelakiNumber.realizeAsAdjective(nounPhrase, this.number);
            throw new NotImplementedException();
        }
    }

}
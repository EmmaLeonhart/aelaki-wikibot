
using System.Runtime.CompilerServices;

namespace General_console
{
    public interface Adjective
    {
        // A read-only property
        string Type { get; }

    }

    internal class StativeAdjective : Adjective
    {
        internal NounPhrase noun;
        private string[] root;

        public StativeAdjective(string c1, string c2, string c3) 
        {
            string[] root = { c1, c2, c3 };
            this.root = root;
        }

        public string Type => "Stative Adjective derived from Verb";

        internal static NumberAdjective AdaptNumber(AelakiNumber number)
        {
            return new NumberAdjective(number);
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
    }

}
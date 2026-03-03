
namespace General_console
{
    internal class Adverb
    {
        internal VerbPhrase verb;
        private string v1;
        private string v2;
        private string v3;
        private string v4;

        public Adverb(string v1, string v2, string v3, string v4)
        {
            this.v1 = v1;
            this.v2 = v2;
            this.v3 = v3;
            this.v4 = v4;
        }

        internal static Adverb FromNumber(int v)
        {
            return new AdverbNumber(v);
            throw new NotImplementedException();
        }

        internal virtual string realize(VerbPhrase verbPhrase)
        {
            throw new NotImplementedException();
        }
    }

    internal class AdverbNumber : Adverb
    {
        private AelakiNumber AelakiNumber;
        const string v1 = "1";
        const string v2 = "2";
        const string v3 = "3";
        const string v4 = "4";
        public AdverbNumber(int v)
            : base(v1, v2, v3, v4)
        {
            this.AelakiNumber = new AelakiNumber(v);
        }

        internal override string realize(VerbPhrase verbPhrase) {
            return AelakiNumber.Adverbial();
            throw new NotImplementedException();
        }
    }
}
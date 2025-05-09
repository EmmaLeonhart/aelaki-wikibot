using AelakiNounGen;
using System.Runtime.CompilerServices;
using System.Security.Cryptography;

namespace General_console
{
    internal class Posessor : StativeAdjective
    {
        private string v1;
        private string v2;
        private string v3;
        private Gender feminine;
        private Person fourth;
        private bool inalienable;
        private Plurality plurality;
        private string v4;

        private static readonly string c1 = "c1";
        private static readonly string c2 = "c2";
        private static readonly string c3 = "c3";

        public Posessor(string v1, string v2, string v3, Gender feminine, Person fourth, Plurality singular, bool alienable) : base(c1, c2, c3)
        {
            this.v1 = v1;
            this.v2 = v2;
            this.v3 = v3;
            this.feminine = feminine;
            this.fourth = fourth;
            this.inalienable = alienable;
            this.plurality = singular;
        }

        public Posessor(string v1, string v2, string v3, string v4, Gender feminine, Person fourth, Plurality singular, bool inalienable) : base(c1, c2, c3)
        {
            this.v1 = v1;
            this.v2 = v2;
            this.v3 = v3;
            this.v4 = v4;
            this.feminine = feminine;
            this.fourth = fourth;
            this.inalienable = inalienable;
            this.plurality = singular;
        }

        public string ToString(Gender posessorGender, Gender posessedGender) {
            if (v4 != null && v4.Length > 0) {
                Console.WriteLine("operating on " + posessorGender.ToString() + " and " + posessedGender.ToString());
                return Noun.BuildPossessor4(this.GetRoot4(), posessorGender, plurality, posessedGender, inalienable);
            }
            else
            {
                throw new NotImplementedException();
            }
        }

        private string[] GetRoot4()
        {
            string[] root = new string[4];
            root[0] = v1;
            root[1] = v2;
            root[2] = v3;
            root[3] = v4;
            return root;
            throw new NotImplementedException();
        }



        internal override string realize(NounPhrase nounPhrase)
        {
            return ToString(this.feminine, nounPhrase.Gender);
            throw new NotImplementedException();
        }

        internal Person getPerson()
        {
            return fourth;
            throw new NotImplementedException();
        }

        internal bool GetAlienable()
        {
            return inalienable;
            throw new NotImplementedException();
        }

        internal Gender getGender()
        {
            return this.feminine;
        }
    }
}
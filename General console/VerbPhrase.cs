namespace General_console
{
    partial class VerbPhrase
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
            return TransitiveVerb.Conjugate(Root, sg, sp, sper, og, op, oper);
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
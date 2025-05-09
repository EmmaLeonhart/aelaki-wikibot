namespace General_console
{
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
                    //Console.WriteLine("Testing adjective");
                    //Console.WriteLine(a.realize(this));
                    s += a.realize(this);
                    s += " ";
                }
            }
            //Console.WriteLine("What we have so far: ");
            //Console.WriteLine(s);
            s += NounPronounciation();
            //Console.WriteLine("What we have so far: ");
            //Console.WriteLine(s);
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
}
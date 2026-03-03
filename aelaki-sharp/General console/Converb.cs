namespace General_console
{
    internal class Converb
    {
        public enum ConverbFunction
        {
            Simultaneous,
            Posterior,
            Anterior,
            Sequential,
            Purposive,
            Causal,
            Conditional,
            Concessive,
            Simulative,
            Terminative,
            Locative,
            SharedCause,
            SharedIntent,
            Instrumental,
            Beneficiary,
            Comitative,
            NextDay    // your new one
        }

        public string Root { get; }
        public ConverbFunction Function { get; }

        public Converb(string root, ConverbFunction function)
        {
            Root = root;
            Function = function;
        }

        public Converb(string v1, string v2, string v3, string v4)
        {
            throw new NotImplementedException();
        }

        private static readonly Dictionary<ConverbFunction, (string prefix, string? suffix, string gloss)> FunctionMap = new()
        {
            { ConverbFunction.Simultaneous,   ("ta", null,         "while doing") },
            { ConverbFunction.Posterior,      ("ngu", "shəlon", "before doing") },
            { ConverbFunction.Anterior,       ("ngu", "mulon",     "after doing") },
            { ConverbFunction.Sequential,     ("ngu", "lon",       "immediately after") },
            { ConverbFunction.Purposive,      ("ki", null,         "in order to") },
            { ConverbFunction.Causal,         ("ha", null,         "because") },
            { ConverbFunction.Conditional,    ("sa", null,         "if") },
            { ConverbFunction.Concessive,     ("ra", null,         "even though") },
            { ConverbFunction.Simulative,     ("tu", null,         "as if") },
            { ConverbFunction.Terminative,    ("", "ndor",        "until") },
            { ConverbFunction.Locative,       ("", "lok",         "where") },
            { ConverbFunction.SharedCause,    ("ha", "s",          "sharing cause") },
            { ConverbFunction.SharedIntent,   ("ki", "s",          "sharing intent") },
            { ConverbFunction.Instrumental,   ("mi", null,         "by means of") },
            { ConverbFunction.Beneficiary,    ("", "rum",         "for the benefit of") },
            { ConverbFunction.Comitative,     ("", "wom",         "together with") },
            { ConverbFunction.NextDay,        ("ngu", "shəłon", "the next day") }  // special case with future + ordinal
        };

        public string Generate()
        {
            var (prefix, suffix, gloss) = FunctionMap[Function];
            return prefix + Root + (suffix ?? "");
        }

        public string Gloss()
        {
            return FunctionMap[Function].gloss;
        }

        public static void ListAll()
        {
            foreach (var kv in FunctionMap)
            {
                Console.WriteLine($"{kv.Key,-15} → {kv.Value.prefix ?? ""}ROOT{(kv.Value.suffix != null ? kv.Value.suffix : "")}  =  {kv.Value.gloss}");
            }
        }
    }
}

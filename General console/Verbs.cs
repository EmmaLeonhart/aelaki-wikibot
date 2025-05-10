using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System;
using System.Collections.Generic;
using System.Text;

/// ------------------------------------------------------------
/// ENUMS: person, number, gender
/// ------------------------------------------------------------
enum Person { First, Second, Third, Fourth }
enum Number { Singular, Plural, Collective, Zero }
enum Gender { Child, Female, Male }

static class AelakiVerbBuilder
{
    // ------------------------------------------------------------------
    // 1.  Gender-Number  →  “gender vowel”  (inside the stem)
    // ------------------------------------------------------------------
    private static readonly Dictionary<(Gender, Number), string> GenderVowel =
        new()
        {
            { (Gender.Child , Number.Singular)   , "u"  },
            { (Gender.Child , Number.Plural)     , "u"  },   // plural uses reduplication later
            { (Gender.Child , Number.Collective) , "i"  },
            { (Gender.Child , Number.Zero)       , "uf" },

            { (Gender.Female, Number.Singular)   , "o"  },
            { (Gender.Female, Number.Plural)     , "o"  },
            { (Gender.Female, Number.Collective) , "e"  },
            { (Gender.Female, Number.Zero)       , "of" },

            { (Gender.Male  , Number.Singular)   , "a"  },
            { (Gender.Male  , Number.Plural)     , "a"  },
            { (Gender.Male  , Number.Collective) , "æ"  },
            { (Gender.Male  , Number.Zero)       , "af" },
        };

    // ------------------------------------------------------------------
    // 2.  Subject-prefix table   (only CHILD gender given so far)
    //     Key: (Person,Number,Gender)   → prefix
    // ------------------------------------------------------------------
    private static readonly Dictionary<(Person, Number, Gender), string> SubjectPrefix =
        new()
        {
            // CHILD
            { (Person.First , Number.Singular  , Gender.Child), "thu"      },
            { (Person.First , Number.Plural    , Gender.Child), "thuthu"   },
            { (Person.First , Number.Collective, Gender.Child), "thi"      },

            { (Person.Second, Number.Singular  , Gender.Child), "ju"      },
            { (Person.Second, Number.Plural    , Gender.Child), "juju"  },
            { (Person.Second, Number.Collective, Gender.Child), "ji"      },

            { (Person.Third , Number.Singular  , Gender.Child), "shu"      },
            { (Person.Third , Number.Plural    , Gender.Child), "shushu"   },
            { (Person.Third , Number.Collective, Gender.Child), "shi"      },

            { (Person.Fourth, Number.Singular  , Gender.Child), "ku"       },
            { (Person.Fourth, Number.Plural    , Gender.Child), "kuku"     },
            { (Person.Fourth, Number.Collective, Gender.Child), "ki"       },
        };
    // ------------------------------------------------------------------
    // 3.  Object-suffix table   (only a few rows filled; extend as needed)
    // ------------------------------------------------------------------
    private static readonly Dictionary<(Person, Number), string> ObjectSuffix =
        new()
        {
            { (Person.First , Number.Singular) , "-uthu"   },
            { (Person.First , Number.Plural)   , "-uthuth" },
            { (Person.First , Number.Collective), "-ithi"  },
            { (Person.First , Number.Zero)     , "-ufuthu" },

            { (Person.Second, Number.Singular) , "-uju"   },
            { (Person.Second, Number.Plural)   , "-ujuju"},
            // fill in more...
        };

    // ------------------------------------------------------------------
    // 4.  Template expansion helper – same dash syntax you used
    // ------------------------------------------------------------------
    private static string ExpandTemplate(string root, string template)
    {
        var sb = new StringBuilder();
        foreach (var token in template.Split('-'))
        {
            if (int.TryParse(token, out int idx))
                sb.Append(root[idx - 1]);               // “1”→C1
            else
                sb.Append(token);
        }
        return sb.ToString();
    }

    // ------------------------------------------------------------------
    // 5.  PUBLIC METHOD  BuildVerb
    // ------------------------------------------------------------------
    public static string BuildVerb(
        string root,
        string stemTemplate,               // e.g. "1-a-2-3-e-r"
        Person subjP, Number subjN, Gender subjG,
        Person objP = Person.Fourth,      // default: no overt object suffix
        Number objN = Number.Singular)
    {
        // (a) subject prefix
        string prefix = SubjectPrefix.TryGetValue((subjP, subjN, subjG), out var pre)
                        ? pre : "";

        // (b) insert gender vowel into template
        string gv = GenderVowel[(subjG, subjN)];
        string templ = stemTemplate.Replace("a", gv);    // “a” slot = gender vowel
        string stem = ExpandTemplate(root, templ);

        // (c) object suffix
        string suffix = ObjectSuffix.TryGetValue((objP, objN), out var suf)
                        ? suf : "";

        return prefix + stem + suffix;
    }
}

/* ---------------------------------------------------
   Quick demo
   ---------------------------------------------------*/
class Demo
{
    static void Demonstration()
    {
        string root = "kmdr";

        // 1) 1st-child-sing subject, 3rd child object, Telic Perfect template
        Console.WriteLine(
            AelakiVerbBuilder.BuildVerb(root, "1-a-2-3-e-r",
                                        Person.First, Number.Singular, Gender.Child,
                                        Person.Third, Number.Singular));
        // ➜  thu + kumder + - (no 3rd-child suffix yet)

        // 2) 2nd-child plural subject acting on 1st-pl object, Habitual template
        Console.WriteLine(
            AelakiVerbBuilder.BuildVerb(root, "1-a-2-3-o-3-o-4",
                                        Person.Second, Number.Plural, Gender.Child,
                                        Person.First, Number.Plural));
        // ➜  jtuju + kumdodor + -uthuth
    }
}

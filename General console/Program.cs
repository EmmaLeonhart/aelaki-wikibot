using System;
using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Metadata.Ecma335;

namespace General_console
{
    class AelakiNumber
    {
        private static readonly string[] Units12 = {
            "", "Pan","Bal","Bhan","Mal","Tan",
            "Dal","Dhan","Nal","Kan","Gal","Ghan","Nger"
        };

        // Ordinal forms for 1..12
        private static readonly string[] Ordinals12 = {
            "", "Sekon","Kezon","Bhalon","Malon","Talon",
            "Dalon","Dhanon","Nalon","Kanon","Galon","Ghanon","Ngeron"
        };

        public int Value { get; private set; }
        public AelakiNumber(int v) => Value = v;

        // prefix ++
        public static AelakiNumber operator ++(AelakiNumber n)
        {
            n.Value++;
            return n;
        }

        public override string ToString() => Cardinal();

        public string Cardinal()
        {
            if (Value <= 0) return Value.ToString();

            // exacjy 60
            if (Value == 60)
                return "Vibhi";

            // 1..12
            if (Value <= 12)
                return Units12[Value];

            // 13..59: base-12 dozens
            if (Value < 60)
            {
                int dozens = Value / 12;
                int rem = Value % 12;
                string part = Units12[dozens] + Units12[12]; // e.g. BalNger
                if (dozens == 1)
                {
                    part = Units12[12];
                }
                return rem == 0
                    ? part
                    : part + Units12[rem];
            }

            // > 60: mixed base-60
            int sixtyCount = Value / 60;
            int rest = Value % 60;
            string head = (sixtyCount == 1 ? "" : new AelakiNumber(sixtyCount).Cardinal())
                        + "Vibhi";
            return rest == 0
                ? head
                : head + new AelakiNumber(rest).Cardinal();
        }


        //public static string Cardinal(int v)
        //{
        //    if (v <= 0) return Value.ToString();

        //    // exacjy 60
        //    if (v == 60)
        //        return "Vibhi";

        //    // 1..12
        //    if (v <= 12)
        //        return Units12[v];

        //    // 13..59: base-12 dozens
        //    if (v < 60)
        //    {
        //        int dozens = v / 12;
        //        int rem = v % 12;
        //        string part = Units12[dozens] + Units12[12]; // e.g. BalNger
        //        return rem == 0
        //            ? part
        //            : part + Units12[rem];
        //    }

        //    // > 60: mixed base-60
        //    int sixtyCount = v / 60;
        //    int rest = v % 60;
        //    string head = (sixtyCount == 1 ? "" : new AelakiNumber(sixtyCount).Cardinal())
        //                + "Vibhi";
        //    return rest == 0
        //        ? head
        //        : head + new AelakiNumber(rest).Cardinal();
        //}

        public string Ordinal()
        {
            if (Value <= 0) return Value.ToString();

            // exacjy 60? treat as 60th
            if (Value == 60)
                return "Vibhisekon";

            // 1..12
            if (Value <= 12)
                return Ordinals12[Value];

            // 13..59: dozens + unit ordinal
            if (Value < 60)
            {
                int dozens = Value / 12;
                int rem = Value % 12;
                string head = Units12[dozens] + Units12[12]; // e.g. BalNger
                if (dozens == 1) { 
                head = Units12[12];
                }
                return head + Ordinals12[rem];
            }

            // > 60: mixed base-60
            int sixtyCount2 = Value / 60;
            int rest2 = Value % 60;
            string head2 = (sixtyCount2 == 1 ? "" : new AelakiNumber(sixtyCount2).Ordinal())
                         + "Vibhi";
            return head2 + new AelakiNumber(rest2).Ordinal();
        }

        public string text()
        {
            return text(this.Value);
        }

        internal static string text(int v)
        {
            if (v == 60)
            {
                return "支金0";
            }
            if (v >= 60)
            {
                int second60 = v / 60;
                int first60 = v % 60;
                return text(second60) + "支" + text(first60);
                throw new NotImplementedException();
            }
            if (v <= 0)
            {
                throw (new NotImplementedException());
            }
            else
            {
                int twelves = v / 12;
                int ones = v % 12;
                string season = GetSeason(twelves);
                string dozenal = GetDozenal(ones);
                return season + dozenal;
            }
        }

        private static string GetDozenal(int ones)
        {
            if (ones >= 0 && ones <= 9)
            {
                return ones.ToString();
            }
            else if (ones == 10)
            {
                return "十";
            }
            else if (ones == 11)
            {
                return "λ";
            }
            else
            {
                Console.WriteLine(ones);
                throw new Exception();
            }

        }

        private static string GetSeason(int twelves)
        {
            switch (twelves)
            {
                case 0:  return "金";  // Metal
                case 1:  return "水";  // Water
                case 2:  return "木";  // Wood
                case 3:  return "火";  // Fire
                case 4:  return "土";  // Earth
                default:
                    Console.WriteLine(twelves);
                    throw new ArgumentOutOfRangeException(
                        nameof(twelves),
                        "Valid codes are 0(金), 1(水), 2(木), 3(火), or 4(土).");
            }
        }

        public static string ToEnglishOrdinal(int n)
        {
            if (n <= 0)
                return n.ToString();

            int rem100 = n % 100;
            // 11th, 12th, 13th are special
            if (rem100 >= 11 && rem100 <= 13)
                return $"{n}th";

            switch (n % 10)
            {
                case 1: return $"{n}st";
                case 2: return $"{n}nd";
                case 3: return $"{n}rd";
                default: return $"{n}th";
            }
        }

        internal string textOrdinal()
        {
            return AppendOrdinalSuffix(text(Value));
        }

        public static string AppendOrdinalSuffix(string input)
        {

            return input + "th";


            if (string.IsNullOrEmpty(input) || !char.IsDigit(input[^1]))
                return input;

            // Check last two digits if possible (for special cases: 11th, 12th, 13th)
            if (input.Length >= 2 && char.IsDigit(input[^2]))
            {
                string lastTwo = input[^2..];
                if (lastTwo == "11" || lastTwo == "12" || lastTwo == "13")
                    return input + "th";
            }

            // Check last digit
            char last = input[^1];
            return last switch
            {
                '1' => input + "st",
                '2' => input + "nd",
                '3' => input + "rd",
                _ => input + "th"
            };
        }

        // English “partitive” :   1 → "one of", 2 → "two of", …  (fallback: "N of")
        public static string EnglishPartitive(int n)
        {
            return n switch
            {
                1 => "one of",
                2 => "two of",
                3 => "three of",
                4 => "four of",
                _ => $"{n} of"
            };
        }

        // Aelaki partitive 1–15  (throw beyond that until you add more)
        private static readonly string[] AelakiPartitives =
        {
            "",        // 0 (unused)
            "Papan",   // 1
            "Babal",   // 2
            "Bhabhan", // 3
            "Mamal",   // 4
            "Tatan",   // 5
            "Dadal",   // 6
            "Dhadhan", // 7
            "Nanal",   // 8
            "Kakan",   // 9
            "Gagal",   //10
            "Ghaghan", //11
            "Ngenger", //12
            "Ngerpapan",   //13
            "Ngerbabal",   //14
            "Ngerbhabhan"  //15
        };

        public static string AelakiPartitive(int n)
        {
            if (n >= 1 && n < AelakiPartitives.Length)
                return AelakiPartitives[n];
            else 
                return GeneratePartitive(n);
            
                throw new ArgumentOutOfRangeException(nameof(n),
                    "Partitives defined only for 1-15 (extend the table for higher numbers).");
        }

        public enum Gender
        {
            Child,   // “u / ü” colour
            Female,  // “o”  colour
            Male     // baseline “a” colour
        }

        public static string GenerateCardinal(Gender g, int n)
        {
            // 1) Get the “male / baseline” cardinal     (Pan, Bal, …  Ngar, Vibhi)
            string baseForm = new AelakiNumber(n).Cardinal();

            // 2) Decide what target vowel we need
            char targetA;   // replacement for baseline ‘a’
            char targetE;   // replacement for baseline ‘e’

            switch (g)
            {
                case Gender.Male:   // keep baseline
                    return baseForm;

                case Gender.Female:
                    targetA = 'o';
                    targetE = 'o';
                    break;

                case Gender.Child:
                    targetA = 'u';
                    targetE = 'ü';   // give /ü/ for baseline e
                    break;

                default:
                    return baseForm;
            }

            // 3) Build a new string, swapping each vowel we care about
            var sb = new System.Text.StringBuilder(baseForm.Length);
            foreach (char c in baseForm)
            {
                switch (char.ToLowerInvariant(c))
                {
                    case 'a': sb.Append(targetA); break;
                    case 'e': sb.Append(targetE); break;
                    default: sb.Append(c); break;   // leave consonants + other vowels alone
                }
            }
            return sb.ToString();
        }

        public static string GenerateCollective(int n)
        {
            return GenerateCardinal(Gender.Male, n)
                .Replace("u", "i")
                .Replace("ü", "ï")
                .Replace("o", "e")
                .Replace("ə", "æ")
                .Replace("a", "æ");
        }

        //ï	üæ	ə

        public static string GeneratePartitive(int n)
        {
            if (n < 1 || n > 60)
                return "Vibhi " + AelakiPartitive(n / 60);
                //throw new ArgumentOutOfRangeException(nameof(n), "Valid range is 1–60.");

            // 60 is a lexical special case
            if (n == 60) return "Vibhibhi";

            // ------------------------------------------------------------------
            // 1.  partitive units (1‒12)
            // ------------------------------------------------------------------
            string[] partUnits = {
        "",          // 0 (unused)
        "Papan",     // 1
        "Babal",     // 2
        "Bhabhan",   // 3
        "Mamal",     // 4
        "Tatan",     // 5
        "Dadal",     // 6
        "Dhadhan",   // 7
        "Nanal",     // 8
        "Kakan",     // 9
        "Gagal",     //10
        "Ghaghan",   //11
        "Ngenger"    //12
    };

            // Base-12 root names (same list used in your cardinals):
            string[] units12 = {
        "", "Pan","Bal","Bhan","Mal","Tan",
        "Dal","Dhan","Nal","Kan","Gal","Ghan","Nger"
    };

            if (n <= 12)
                return partUnits[n];

            // ------------------------------------------------------------------
            // 2.  13‒59
            // ------------------------------------------------------------------
            int dozens = n / 12;   // 1,2,3,4
            int remainder = n % 12;  // 1‥11  (0 means exact dozen)

            // 2.a  Exact dozens 24, 36, 48  →  BalNgenger, BhanNgenger, MalNgenger
            if (remainder == 0)
                return units12[dozens] + "Ngenger";

            // 2.b  Non-zero remainder:
            //      • 13–23  →  Nger + unit-partitive
            //      • 25–59  →  <DozenName> + Nger + unit-partitive
            string prefix = dozens == 1
                ? "Nger"
                : units12[dozens] + "Nger";

            return prefix + partUnits[remainder];
        }

        internal object Partitive()
        {
            return AelakiPartitive(Value);
        }

        internal string Collective()
        {
            return GenerateCollective(Value);
            throw new NotImplementedException();
        }

        internal static string EnglishCollective(int i)
        {
            return "all " + i;
            throw new NotImplementedException();
        }
    }

    class Program
    {
        static void Main()
        {
            var n = new AelakiNumber(1);
            Console.OutputEncoding = System.Text.Encoding.UTF8;
            Console.WriteLine("1–60:");
            for (int i = 1; i <= 63; i++, n++)
            {
                Console.WriteLine("=====" + i + "=====");
                Console.WriteLine($"Cardinal: {i} → {n.text()} → {n.Cardinal()}");
                Console.WriteLine($"Ordinal:  {AelakiNumber.ToEnglishOrdinal(i)} → {n.textOrdinal()} → {n.Ordinal()}");
                Console.WriteLine($"Partitive:  {AelakiNumber.EnglishPartitive(i)} → {n.text()} → {n.Partitive()}");
                Console.WriteLine($"Collective:  {AelakiNumber.EnglishCollective(i)} → {n.text()} → {n.Collective()}");
            }
        }
    }
}

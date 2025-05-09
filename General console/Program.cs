using System;
using System.Collections.Generic;

namespace General_console
{
    class AelakiNumber
    {
        private static readonly string[] Units12 = {
            "", "Pan","Bal","Bhan","Mal","Tan",
            "Dal","Dhan","Nal","Kan","Gal","Ghan","Nger"
        };

        public int Value { get; private set; }
        public AelakiNumber(int v) => Value = v;

        // prefix ++
        public static AelakiNumber operator ++(AelakiNumber n)
        {
            n.Value++;
            return n;
        }

        public override string ToString()
        {
            if (Value <= 0) return Value.ToString();

            // exactly 60
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
                return rem == 0
                    ? part
                    : part + Units12[rem];  // e.g. NgerPan or BalNgerPan
            }

            // > 60: mixed base-60
            int sixtyCount = Value / 60;
            int rest = Value % 60;
            string head = (sixtyCount == 1 ? "" : new AelakiNumber(sixtyCount).ToString())
                        + "Vibhi";
            return rest == 0
                ? head
                : head + new AelakiNumber(rest).ToString();
        }

        internal string text()
        {
            if (Value == 60)
            {
                return "支金0";
            }
            if (Value >= 60)
            {

                throw new NotImplementedException();
            }
            if (Value <= 0)
            {
                throw (new NotImplementedException());
            }
            else
            {
                int twelves = Value / 12;
                int ones = Value % 12;
                string season = GetSeason(twelves);
                string dozenal = GetDozenal(ones);
                return season + dozenal;
            }
            throw new NotImplementedException();
        }

        private string GetDozenal(int ones)
        {
            if (ones >= 0 && ones <= 9)
            {
                // ones is in range 0–9
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

        private string GetSeason(int twelves)
        {
            switch (twelves)
            {
                case 0:  // Metal
                    return "金";
                case 1:  // Water
                    return "水";
                case 2:  // Wood
                    return "木";
                case 3:  // Fire
                    return "火";
                case 4:  // Earth
                    return "土";
                default:
                    Console.WriteLine(twelves);
                    throw new ArgumentOutOfRangeException(
                        nameof(twelves),
                        "Valid codes are 0(金), 1(水), 2(木), 3(火), or 4(土).");
            }
        }
    }

    class Program
    {
        static void Main()
        {
            // Demonstration
            var n = new AelakiNumber(1);
            Console.OutputEncoding = System.Text.Encoding.UTF8;
            Console.WriteLine("1–60:");
            for (int i = 1; i <= 60; i++, n++)
            {
                Console.WriteLine($"{i} → {n.text()} → {n}");
            }

            // your specific examples
            //Console.WriteLine();
            //foreach (var v in new[] { 24, 36, 48, 60, 61 })
            //{
            //    Console.WriteLine($"{v} → {new AelakiNumber(v)}");
            //}
        }
    }
}

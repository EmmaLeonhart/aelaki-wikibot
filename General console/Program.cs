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
    }

    class Program
    {
        static void Main()
        {
            // Demonstration
            var n = new AelakiNumber(1);
            Console.OutputEncoding = System.Text.Encoding.UTF8;
            Console.WriteLine("1–15:");
            for (int i = 1; i <= 15; i++, n++)
            {
                Console.WriteLine($"{i} → {n}");
            }

            // your specific examples
            Console.WriteLine();
            foreach (var v in new[] { 24, 36, 48, 60, 61 })
            {
                Console.WriteLine($"{v} → {new AelakiNumber(v)}");
            }
        }
    }
}

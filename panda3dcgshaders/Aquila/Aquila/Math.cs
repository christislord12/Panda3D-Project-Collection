namespace Aquila
{
    public class Math
    {
        public static float DegreeToRadian(float angle)
        {
            return Math.PI * angle / 180.0f;
        }

        public static float RadianToDegree(float angle)
        {
            return angle * 180.0f / Math.PI;
        }

        public static void Swap<T>(ref T left, ref T right)
        {
            T t;
            t = left;
            left = right;
            right = t;
        }

        public static float Clamp(float value, float min, float max)
        {
            if (value < min)
            {
                return min;
            }
            else if (value > max)
            {
                return max;
            }
            else
            {
                return value;
            }
        }

        public static int Clamp(int value, int min, int max)
        {
            if (value < min)
            {
                return min;
            }
            else if (value > max)
            {
                return max;
            }
            else
            {
                return value;
            }
        }

        public static float Saturate(float value)
        {
            if (value <= 0.0f)
            {
                return 0.0f;
            }
            else if (value >= 1.0f)
            {
                return 1.0f;
            }
            else
            {
                return value;
            }
        }

        public static float Pow(double baze, double exponent)
        {
            return (float)System.Math.Pow(baze, exponent);
        }

        public static float Sqrt(float value)
        {
            return (float)System.Math.Sqrt(value);
        }

        public static float Sin(float value)
        {
            return (float)System.Math.Sin(value);
        }

        public static float Cos(float value)
        {
            return (float)System.Math.Cos(value);
        }

        public static float Tan(float value)
        {
            return (float)System.Math.Tan(value);
        }

        public static float Cot(float value)
        {
            return 1.0f / (float)System.Math.Tan(value);
        }

        public static bool IsAlmostEqual(float a, float b, float epsilon)
        {
            float delta = a - b;
            return (delta < epsilon) && (delta > -epsilon);
        }

        public static bool IsAlmostEqual(float a, float b)
        {
            float delta = a - b;
            return (delta < EPSILON) && (delta > -EPSILON);
        }

        public const float PI = (float)System.Math.PI;

        public const float EPSILON = 1.0e-6f;

        public static float Floor(float value)
        {
            return (float) System.Math.Floor(value);
        }

        public static float Ceiling(float value)
        {
            return (float)System.Math.Ceiling(value);
        }
    }
}

namespace Aquila
{
    public struct Vector3 : LinearInterpolation<Vector3>
    {
        private float e0;
        private float e1;
        private float e2;

        public float X
        {
            get { return this.e0; }
            set { this.e0 = value; }
        }

        public float Y
        {
            get { return this.e1; }
            set { this.e1 = value; }
        }

        public float Z
        {
            get { return this.e2; }
            set { this.e2 = value; }
        }

        public float R
        {
            get { return this.e0; }
            set { this.e0 = value; }
        }

        public float G
        {
            get { return this.e1; }
            set { this.e1 = value; }
        }

        public float B
        {
            get { return this.e2; }
            set { this.e2 = value; }
        }

        public float S
        {
            get { return this.e0; }
            set { this.e0 = value; }
        }

        public float T
        {
            get { return this.e1; }
            set { this.e1 = value; }
        }

        public float P
        {
            get { return this.e2; }
            set { this.e2 = value; }
        }

        public Vector3(float e0, float e1, float e2)
        {
            this.e0 = e0;
            this.e1 = e1;
            this.e2 = e2;
        }

        public Vector3(Vector3 vector)
        {
            this.e0 = vector.e0;
            this.e1 = vector.e1;
            this.e2 = vector.e2;
        }

        public string Pretty()
        {
            return string.Format("{0}({1}, {2}, {3})",
                this.GetType().Name, this.e0, this.e1, this.e2);
        }

        public void Add(float value)
        {
            this.e0 += value;
            this.e1 += value;
            this.e2 += value;
        }

        public void Subtract(float value)
        {
            this.e0 -= value;
            this.e1 -= value;
            this.e2 -= value;
        }

        public void Multiply(float value)
        {
            this.e0 *= value;
            this.e1 *= value;
            this.e2 *= value;
        }

        public void Divide(float value)
        {
            this.e0 *= value;
            this.e1 *= value;
            this.e2 *= value;
        }

        public float SquaredLength()
        {
            return this.e0 * this.e0 + this.e1 * this.e1 + this.e2 * this.e2;
        }

        public float Length()
        {
            return Math.Sqrt(this.e0 * this.e0 + this.e1 * this.e1 + this.e2 * this.e2);
        }

        public void Normalize()
        {
            float length = Length();
            Multiply(1.0f / length);
        }

        public static float Dot(Vector3 vector1, Vector3 vector2)
        {
            return vector1.e0 * vector2.e0 + vector1.e1 * vector2.e1 + vector1.e2 * vector2.e2;
        }

        public static Vector3 Cross(Vector3 vector1, Vector3 vector2)
        {
            Vector3 result;
            result.e0 = vector1.e1 * vector2.e2 + vector1.e2 * vector2.e1;
            result.e1 = vector1.e2 * vector2.e0 + vector1.e0 * vector2.e2;
            result.e2 = vector1.e0 * vector2.e1 + vector1.e1 * vector2.e0;
            return result;
        }

        public void LinearInterpolate(Vector3 vector1, Vector3 vector2, float control)
        {
            float c1 = 1.0f - control;
            float c2 = control;
            this.e0 = vector1.e0 * c1 + vector2.e0 * c2;
            this.e1 = vector1.e1 * c1 + vector2.e1 * c2;
            this.e2 = vector1.e2 * c1 + vector2.e2 * c2;
        }
    }
}

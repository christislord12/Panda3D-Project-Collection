namespace Aquila
{
    public struct Vector1 : LinearInterpolation<Vector1>
    {
        private float e0;

        public float X
        {
            get { return this.e0; }
            set { this.e0 = value; }
        }

        public float R
        {
            get { return this.e0; }
            set { this.e0 = value; }
        }

        public float S
        {
            get { return this.e0; }
            set { this.e0 = value; }
        }

        public Vector1(float e0)
        {
            this.e0 = e0;
        }

        public Vector1(Vector1 vector)
        {
            this.e0 = vector.e0;
        }

        public string Pretty()
        {
            return string.Format("{0}({1})",
                this.GetType().Name, this.e0);
        }

        public void LinearInterpolate(Vector1 vector1, Vector1 vector2, float control)
        {
            float c1 = 1.0f - control;
            float c2 = control;
            this.e0 = vector1.e0 * c1 + vector2.e0 * c2;
        }
    }
}

namespace Aquila
{
    public class Texture2<T> where T : LinearInterpolation<T>, new()
    {
        public enum Wrap
        {
            NONE,
            CLAMP,
            BORDER,
            REPEAT,
            REPEAT_MIRROR,
        }

        public enum Interpolation
        {
            NONE,
            LINEAR,
        }

        private Timer timerClear = Profiler.Instance.CreateTimer("Clear");

        private T[,] buffer;
        private int width;
        private int height;
        private float widthTexel;
        private float heightTexel;
        private T border;
        private Wrap wrapS = Wrap.REPEAT_MIRROR;
        private Wrap wrapT = Wrap.REPEAT_MIRROR;
        private Interpolation interpolate = Interpolation.LINEAR;

        public Texture2(int width, int height)
        {
            this.width = width;
            this.height = height;
            this.widthTexel = width - 1.0f;
            this.heightTexel = height - 1.0f;
            this.buffer = new T[height, width];
        }

        public int Width
        {
            get { return this.width; }
        }

        public int Height
        {
            get { return this.height; }
        }

        public Wrap WrapS
        {
            get { return this.wrapS; }
            set { this.wrapS = value; }
        }

        public Wrap WrapT
        {
            get { return this.wrapT; }
            set { this.wrapT = value; }
        }

        public Interpolation Interpolate
        {
            get { return this.interpolate; }
            set { this.interpolate = value; }
        }

        /// <summary>
        /// This method consumes ~7 ms on my 2 GHz CPU with a 640 x 480 buffer.
        /// Try to avoid this method if possible. E.g. if your scene fills the
        /// whole screen anyway, then there is no need to clear color buffer.
        /// </summary>
        public void Clear(T value)
        {
            timerClear.Start();

            for (int y = 0; y < this.height; y++)
            {
                for (int x = 0; x < this.width; x++)
                {
                    this.buffer[y, x] = value;
                }
            }

            timerClear.Stop();
        }

        public void SetBorder(T border)
        {
            this.border = border;
        }

        public T GetTexel(Vector2 vector)
        {
            float s = 0.0f;
            float t = 0.0f;

            if (wrapS == Wrap.NONE)
            {
                s = vector.S;
            }
            else if (wrapS == Wrap.CLAMP)
            {
                s = Math.Saturate(vector.S);
            }
            else if (wrapS == Wrap.BORDER)
            {
                if ((vector.S >= 0.0f) && (vector.S <= 1.0f))
                {
                    s = vector.S;
                }
                else
                {
                    return this.border;
                }
            }
            else if (wrapS == Wrap.REPEAT)
            {
                s = vector.S % 1.0f;
                if (s < 0.0f)
                {
                    s += 1.0f;
                }
            }
            else if (wrapS == Wrap.REPEAT_MIRROR)
            {
                s = vector.S % 2.0f;
                if (s < 0.0f)
                {
                    s += 2.0f;
                }
                if (s > 1.0f)
                {
                    s = 2.0f - s;
                }
            }

            if (wrapT == Wrap.NONE)
            {
                t = vector.T;
            }
            else if (wrapT == Wrap.CLAMP)
            {
                t = Math.Saturate(vector.T);
            }
            else if (wrapT == Wrap.BORDER)
            {
                if ((vector.T >= 0.0f) && (vector.T <= 1.0f))
                {
                    t = vector.T;
                }
                else
                {
                    return this.border;
                }
            }
            else if (wrapT == Wrap.REPEAT)
            {
                t = vector.T % 1.0f;
                if (t < 0.0f)
                {
                    t += 1.0f;
                }
            }
            else if (wrapT == Wrap.REPEAT_MIRROR)
            {
                t = vector.T % 2.0f;
                if (t < 0.0f)
                {
                    t += 2.0f;
                }
                if (t > 1.0f)
                {
                    t = 2.0f - t;
                }
            }

            if (interpolate == Interpolation.NONE)
            {
                int x = (int)(this.widthTexel * s);
                int y = (int)(this.heightTexel * t);
                return this.buffer[y, x];
            }
            else if (interpolate == Interpolation.LINEAR)
            {
                int x1 = (int)Math.Floor(this.widthTexel * s);
                int x2 = (int)Math.Ceiling(this.widthTexel * s);

                float controlx = this.widthTexel * s - x1;

                int y1 = (int)Math.Floor(this.heightTexel * t);
                int y2 = (int)Math.Ceiling(this.heightTexel * t);

                float controly = this.heightTexel * t - y1;

                T c1 = this.buffer[y1, x1];
                T c2 = this.buffer[y1, x2];
                T c3 = this.buffer[y2, x1];
                T c4 = this.buffer[y2, x2];

                T c12 = this.border;
                c12.LinearInterpolate(c1, c2, controlx);

                T c34 = this.border;
                c34.LinearInterpolate(c3, c4, controlx);

                T c1234 = this.border;
                c1234.LinearInterpolate(c12, c34, controly);

                return c1234;
            }
            else
            {
                return this.border;
            }
        }

        public T GetPixel(int x, int y)
        {
            return this.buffer[y, x];
        }

        public void SetPixel(int x, int y, T value)
        {
            this.buffer[y, x] = value;
        }
    }
}

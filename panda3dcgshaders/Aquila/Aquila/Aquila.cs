using System.Runtime.InteropServices;

namespace Aquila
{
    public interface Varying
    {
        void Load(float[] values);
        void Store(float[] values);
        int Elements();
    }

    /// <summary>
    /// This interface is a bit odd, because C# does not allow static methods in
    /// interfacess (the CLR does BTW).
    /// </summary>
    public interface LinearInterpolation<T>
    {
        void LinearInterpolate(T vector1, T vector2, float control);
    }

    public class Aquila
    {
        private Texture2<Vector4> colorBuffer;
        private Texture2<Vector1> depthBuffer;

        private Vector4 clearColor = new Vector4(0.7f, 0.8f, 0.9f, 1.0f);
        private Vector1 clearDepth = new Vector1(1.0f);

        private Timer timerDrawTriangles = Profiler.Instance.CreateTimer("DrawTriangles");

        private int viewportX;
        private int viewportY;
        private int viewportWidth;
        private int viewportHeight;

        private bool perspectiveCorrection = true;

        public Aquila(Texture2<Vector4> colorBuffer, Texture2<Vector1> depthBuffer)
        {
            this.colorBuffer = colorBuffer;
            this.depthBuffer = depthBuffer;

            SetViewport(0, 0, colorBuffer.Width, colorBuffer.Height);
        }

        public void SetPerspectiveCorrection(bool enable)
        {
            this.perspectiveCorrection = enable;
        }

        public void SetClearColor(Vector4 color)
        {
            this.clearColor = color;
        }

        public void SetClearDepth(Vector1 depth)
        {
            this.clearDepth = depth;
        }

        public void ClearColor()
        {
            this.colorBuffer.Clear(this.clearColor);
        }

        public void ClearDepth()
        {
            this.depthBuffer.Clear(this.clearDepth);
        }

        // http://www.opengl.org/sdk/docs/man/xhtml/glViewport.xml
        private void SetViewport(int x, int y, int width, int height)
        {
            this.viewportX = x;
            this.viewportY = y;
            this.viewportWidth = width;
            this.viewportHeight = height;
        }

        private void Viewport(ref Vector4 vector)
        {
            vector.X = (vector.X + 1.0f) * (this.viewportWidth * 0.5f) + this.viewportX;
            vector.Y = (-vector.Y + 1.0f) * (this.viewportHeight * 0.5f) + this.viewportY;
            vector.Z = (vector.Z + 1.0f) * 0.5f;
            //vector.W = vector.W;
        }

        public delegate Vector4 VertexProgramDelegate<U, V, W>(U uniform, V vertex, W varying);
        public delegate Vector4 FragmentProgramDelegate<U, W>(U uniform, W varying);

        // Currently I have no better idea than to create an empty type, or you have to define all types yourself, somehow C# can not inferre the type here.

        /// <summary>
        /// Every parameter should be obvious (if you know OpenGL/DirectX a bit)
        /// except the varying parameter. This parameter is only here, so the C#
        /// can inferre the type of W automatically. If we omit this type here,
        /// you the specify all types for DrawTriangles by yourself.
        /// </summary>
        public void DrawTriangles<U, V, W>(VertexProgramDelegate<U, V, W> vertexProgram, FragmentProgramDelegate<U, W> fragmentProgram, U uniform, V[] vertices, W varying) where W : Varying
        {
            timerDrawTriangles.Start();

            Vector4[] positions = new Vector4[3];

            float[][] varyings = new float[3][];
            int length = varying.Elements();
            for (int i = 0; i < 3; i++)
            {
                varyings[i] = new float[length];
            }

            for (int i = 0; i < vertices.Length; i += 3)
            {
                for (int j = 0; j < 3; j++)
                {
                    positions[j] = vertexProgram(uniform, vertices[i + j], varying);
                    positions[j].HomogenousDivide();
                    Viewport(ref positions[j]);
                    varying.Store(varyings[j]);
                }

                // Sort the three vertices of a triangle along the y axis from top to down. Simplifies the method that does the real work.

                int i0 = 0;
                int i1 = 1;
                int i2 = 2;

                if (positions[i0].Y > positions[i1].Y)
                {
                    Math.Swap(ref i0, ref i1);
                }
                if (positions[i1].Y > positions[i2].Y)
                {
                    Math.Swap(ref i1, ref i2);
                }
                if (positions[i0].Y > positions[i1].Y)
                {
                    Math.Swap(ref i0, ref i1);
                }

                RasterizeTriangle(positions[i0], positions[i1], positions[i2], varyings[i0], varyings[i1], varyings[i2], uniform, fragmentProgram, varying);
            }

            timerDrawTriangles.Stop();
        }

        private void RasterizeTriangle<U, W>(Vector4 p0, Vector4 p1, Vector4 p2, float[] v0, float[] v1, float[] v2, U uniforms, FragmentProgramDelegate<U, W> fragmentProgram, W varying) where W : Varying
        {
            // TODO no OpenGL fill convention

            int length = varying.Elements();

            int width = this.colorBuffer.Width;
            int height = this.colorBuffer.Height;

            int x0 = (int)p0.X;
            int y0 = (int)p0.Y;
            float z0 = p0.Z;
            float w0 = p0.W;

            int x1 = (int)p1.X;
            int y1 = (int)p1.Y;
            float z1 = p1.Z;
            float w1 = p1.W;

            int x2 = (int)p2.X;
            int y2 = (int)p2.Y;
            float z2 = p2.Z;
            float w2 = p2.W;

            if (this.perspectiveCorrection)
            {
                for (int i = 0; i < length; i++)
                {
                    v0[i] *= w0;
                    v1[i] *= w1;
                    v2[i] *= w2;
                }
            }

            float xslope0to1 = (float)(x0 - x1) / (float)(y0 - y1);
            float xslope0to2 = (float)(x0 - x2) / (float)(y0 - y2);
            float xslope1to2 = (float)(x1 - x2) / (float)(y1 - y2);
            // float xslope0to1 = (p0.X - p1.X) / (p0.Y - p1.Y);
            // float xslope0to2 = (p0.X - p2.X) / (p0.Y - p2.Y);
            // float xslope1to2 = (p1.X - p2.X) / (p1.Y - p2.Y);
            float zslope0to1 = (z0 - z1) / (y0 - y1);
            float zslope0to2 = (z0 - z2) / (y0 - y2);
            float zslope1to2 = (z1 - z2) / (y1 - y2);
            float wslope0to1 = (w0 - w1) / (y0 - y1);
            float wslope0to2 = (w0 - w2) / (y0 - y2);
            float wslope1to2 = (w1 - w2) / (y1 - y2);
            float[] vslope0to1 = new float[length];
            float[] vslope0to2 = new float[length];
            float[] vslope1to2 = new float[length];
            for (int i = 0; i < length; i++)
            {
                vslope0to1[i] = (v0[i] - v1[i]) / (y0 - y1);
                vslope0to2[i] = (v0[i] - v2[i]) / (y0 - y2);
                vslope1to2[i] = (v1[i] - v2[i]) / (y1 - y2);
            }

            int x0to1;
            int x0to2;
            int x1to2;
            float z0to1;
            float z0to2;
            float z1to2;
            float w0to1;
            float w0to2;
            float w1to2;
            float[] v0to1 = new float[length];
            float[] v0to2 = new float[length];
            float[] v1to2 = new float[length];

            int xmin;
            int xmax;
            float zmin;
            float zmax;
            float wmin;
            float wmax;
            float[] vmin;
            float[] vmax;
            float zslope;
            float wslope;
            float[] vslope = new float[length];

            float z;
            float w;
            float[] v = new float[length];

            // Theoretically more than one multiplication can be moved out of this loop. Practically it is slower.
            for (int y = y0; y < y1; y++)
            {
                x0to1 = (int)(x1 + xslope0to1 * (y - y1));
                x0to2 = (int)(x2 + xslope0to2 * (y - y2));
                z0to1 = z1 + zslope0to1 * (y - y1);
                z0to2 = z2 + zslope0to2 * (y - y2);
                w0to1 = w1 + wslope0to1 * (y - y1);
                w0to2 = w2 + wslope0to2 * (y - y2);
                for (int i = 0; i < length; i++)
                {
                    v0to1[i] = v1[i] + vslope0to1[i] * (y - y1);
                    v0to2[i] = v2[i] + vslope0to2[i] * (y - y2);
                }

                if (x0to1 > x0to2)
                {
                    xmax = x0to1;
                    xmin = x0to2;
                    zmax = z0to1;
                    zmin = z0to2;
                    wmax = w0to1;
                    wmin = w0to2;
                    vmax = v0to1;
                    vmin = v0to2;
                }
                else
                {
                    xmax = x0to2;
                    xmin = x0to1;
                    zmax = z0to2;
                    zmin = z0to1;
                    wmax = w0to2;
                    wmin = w0to1;
                    vmax = v0to2;
                    vmin = v0to1;
                }

                zslope = (zmax - zmin) / (xmax - xmin);
                wslope = (wmax - wmin) / (xmax - xmin);
                for (int i = 0; i < length; i++)
                {
                    vslope[i] = (vmax[i] - vmin[i]) / (xmax - xmin);
                }

                for (int x = xmin; x < xmax; x++)
                {
                    z = zmin + zslope * (x - xmin);
                    w = wmin + wslope * (x - xmin);
                    for (int i = 0; i < length; i++)
                    {
                        v[i] = vmin[i] + vslope[i] * (x - xmin);
                    }

                    w = 1.0f / w;

                    if (this.perspectiveCorrection)
                    {
                        for (int i = 0; i < length; i++)
                        {
                            v[i] *= w;
                        }
                    }

                    if ((x >= 0) && (y >= 0) && (x < width) && (y < height) && (z >= 0.0f) && (z <= 1.0f))
                    {
                        if (z < depthBuffer.GetPixel(x, y).X)
                        {
                            varying.Load(v);
                            colorBuffer.SetPixel(x, y, fragmentProgram(uniforms, varying));
                            depthBuffer.SetPixel(x, y, new Vector1(z));
                        }
                    }
                }
            }

            for (int y = y1; y < y2; y++)
            {
                x1to2 = (int)(x2 + xslope1to2 * (y - y2));
                x0to2 = (int)(x2 + xslope0to2 * (y - y2));
                z1to2 = z2 + zslope1to2 * (y - y2);
                z0to2 = z2 + zslope0to2 * (y - y2);
                w1to2 = w2 + wslope1to2 * (y - y2);
                w0to2 = w2 + wslope0to2 * (y - y2);
                for (int i = 0; i < length; i++)
                {
                    v1to2[i] = v2[i] + vslope1to2[i] * (y - y2);
                    v0to2[i] = v2[i] + vslope0to2[i] * (y - y2);
                }

                if (x1to2 > x0to2)
                {
                    xmax = x1to2;
                    xmin = x0to2;
                    zmax = z1to2;
                    zmin = z0to2;
                    wmax = w1to2;
                    wmin = w0to2;
                    vmax = v1to2;
                    vmin = v0to2;
                }
                else
                {
                    xmax = x0to2;
                    xmin = x1to2;
                    zmax = z0to2;
                    zmin = z1to2;
                    wmax = w0to2;
                    wmin = w1to2;
                    vmax = v0to2;
                    vmin = v1to2;
                }

                zslope = (zmax - zmin) / (xmax - xmin);
                wslope = (wmax - wmin) / (xmax - xmin);
                for (int i = 0; i < length; i++)
                {
                    vslope[i] = (vmax[i] - vmin[i]) / (xmax - xmin);
                }

                for (int x = xmin; x < xmax; x++)
                {
                    z = zmin + zslope * (x - xmin);
                    w = wmin + wslope * (x - xmin);
                    for (int i = 0; i < length; i++)
                    {
                        v[i] = vmin[i] + vslope[i] * (x - xmin);
                    }

                    w = 1.0f / w;

                    if (this.perspectiveCorrection)
                    {
                        for (int i = 0; i < length; i++)
                        {
                            v[i] *= w;
                        }
                    }

                    if ((x >= 0) && (y >= 0) && (x < width) && (y < height) && (z >= 0.0f) && (z <= 1.0f))
                    {
                        if (z < depthBuffer.GetPixel(x, y).X)
                        {
                            varying.Load(v);
                            colorBuffer.SetPixel(x, y, fragmentProgram(uniforms, varying));
                            depthBuffer.SetPixel(x, y, new Vector1(z));
                        }
                    }
                }
            }
        }
    }
}

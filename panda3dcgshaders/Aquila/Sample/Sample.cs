using System;
using System.Diagnostics;
using System.Drawing;
using System.Windows.Forms;
using Aquila;

namespace Aquila
{
    public partial class Sample : Form
    {
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new Sample());
        }

        private Stopwatch sw = new Stopwatch();
        private float angle = 0.0f;
        private Bitmap bitmap;
        private Texture2<Vector4> colorBuffer;
        private Texture2<Vector1> depthBuffer;
        private Aquila aquila;
        private Matrix4 perspective = new Matrix4();
        private Matrix4 translation = new Matrix4();
        private Matrix4 rotation = new Matrix4();
        private Matrix4 modelViewProjection = new Matrix4();
        //private PositionColorVertex[] vertices = new PositionColorVertex[6];
        private PositionNormalTexcoordVertex[] vertices;
        private Texture2<Vector4> texture;
        private MatrixTextureUniform uniform = new MatrixTextureUniform();

        //private float movingAverage = 100.0f;
        private Profiler profiler = Profiler.Instance;
        private Timer timer = Profiler.Instance.CreateTimer("Sample");

        public Sample()
        {
            InitializeComponent();

            int width = 640;
            int height = 480;

            bitmap = new Bitmap(width, height);
            colorBuffer = new Texture2<Vector4>(width, height);
            depthBuffer = new Texture2<Vector1>(width, height);
            aquila = new Aquila(colorBuffer, depthBuffer);

            //Bitmap textureBitmap = new Bitmap("../../../../circle.png");
            Bitmap textureBitmap = new Bitmap("../../../../arrow.png");
            texture = new Texture2<Vector4>(textureBitmap.Width, textureBitmap.Height);
            TextureUtility.LoadFromRGB(texture, textureBitmap);

            pictureBox1.Image = bitmap;

            // colorized so colors could be used as texture coordinates

            /*
            vertices[0] = new PositionColorVertex(new Vector4(-1.0f, -1.0f, -1.0f, 1.0f), new Vector4(0.0f, 0.0f, 0.0f, 1.0f));
            vertices[1] = new PositionColorVertex(new Vector4(+1.0f, -1.0f, -1.0f, 1.0f), new Vector4(0.0f, 1.0f, 0.0f, 1.0f));
            vertices[2] = new PositionColorVertex(new Vector4(+1.0f, -1.0f, +1.0f, 1.0f), new Vector4(1.0f, 1.0f, 0.0f, 1.0f));
            vertices[3] = new PositionColorVertex(new Vector4(-1.0f, -1.0f, -1.0f, 1.0f), new Vector4(0.0f, 0.0f, 0.0f, 1.0f));
            vertices[4] = new PositionColorVertex(new Vector4(+1.0f, -1.0f, +1.0f, 1.0f), new Vector4(1.0f, 1.0f, 0.0f, 1.0f));
            vertices[5] = new PositionColorVertex(new Vector4(-1.0f, -1.0f, +1.0f, 1.0f), new Vector4(1.0f, 0.0f, 0.0f, 1.0f));
            */
 
            // gradient (perspective correction is better visible)

            /*
            vertices[0] = new PositionColorVertex(new Vector4(-1.0f, -1.0f, -1.0f, 1.0f), new Vector4(1.0f, 0.0f, 0.0f, 1.0f));
            vertices[1] = new PositionColorVertex(new Vector4(+1.0f, -1.0f, -1.0f, 1.0f), new Vector4(1.0f, 0.0f, 0.0f, 1.0f));
            vertices[2] = new PositionColorVertex(new Vector4(+1.0f, -1.0f, +1.0f, 1.0f), new Vector4(0.0f, 0.0f, 1.0f, 1.0f));
            vertices[3] = new PositionColorVertex(new Vector4(-1.0f, -1.0f, -1.0f, 1.0f), new Vector4(1.0f, 0.0f, 0.0f, 1.0f));
            vertices[4] = new PositionColorVertex(new Vector4(+1.0f, -1.0f, +1.0f, 1.0f), new Vector4(0.0f, 0.0f, 1.0f, 1.0f));
            vertices[5] = new PositionColorVertex(new Vector4(-1.0f, -1.0f, +1.0f, 1.0f), new Vector4(0.0f, 0.0f, 1.0f, 1.0f));
            */

            // load external file

            vertices = WavefrontObject.Load("cube.obj"); // 36 vertices
            //vertices = WavefrontObject.Load("sphere.obj"); // 15000 vertices
            //vertices = WavefrontObject.Load("monkey.obj"); // 188000 vertices

            label1.Text = vertices.Length + " vertices";
        }

        private Vector4 VertexProgramSimple(Matrix4 modelViewProjection, PositionColorVertex vertex, ColorVarying varying)
        {
            Vector4 position = modelViewProjection * vertex.position;
            varying.color = vertex.color;
            return position;
        }

        private Vector4 FragmentProgramSimple(Matrix4 modelViewProjection, ColorVarying varying)
        {
            Vector4 color = varying.color;
            return color;
        }

        private Vector4 VertexProgramModel(MatrixTextureUniform uniform, PositionNormalTexcoordVertex vertex, NormalTexcoordVarying varying)
        {
            Vector4 position = uniform.matrix * vertex.position;
            //varying.normal = vertex.normal;
            varying.texcoord = vertex.texcoord;
            return position;
        }

        private Vector4 FragmentProgramModel(MatrixTextureUniform uniform, NormalTexcoordVarying varying)
        {
            //Vector4 color = new Vector4(varying.texcoord.S, varying.texcoord.T, 0.0f, 1.0f);
            Vector4 color = uniform.texture.GetTexel(varying.texcoord);
            //Vector4 color = new Vector4(1.0f, 0.0f, 1.0f, 1.0f);
            return color;
        }

        // TODO FOV is not exactly like Panda3D, currently don't know why
        private void Render()
        {
            float fov = Math.DegreeToRadian(45.0f);
            float aspectRatio = (float)colorBuffer.Width / (float)colorBuffer.Height;

            // to test the near and far plane we limit the z range
            perspective = MatrixUtility.Perspective(fov, aspectRatio, 3.7f, 6.3f);
            translation = MatrixUtility.Translate(new Vector3(0.0f, 0.0f, -5.0f));
            rotation = MatrixUtility.Rotate(angle, new Vector3(0.0f, 1.0f, 0.0f));

            modelViewProjection.Identity();
            modelViewProjection.Multiply(perspective);
            modelViewProjection.Multiply(translation);
            modelViewProjection.Multiply(rotation);

            uniform.matrix = modelViewProjection;
            uniform.texture = texture;

            aquila.ClearColor();
            aquila.ClearDepth();

            aquila.DrawTriangles(VertexProgramModel, FragmentProgramModel, uniform, vertices, new NormalTexcoordVarying());
            //aquila.DrawTriangles(VertexProgramSimple, FragmentProgramSimple, modelViewProjection, vertices, new ColorVarying());

            TextureUtility.SaveToRGB(colorBuffer, bitmap);
            //TextureUtility.SaveToRGB(depthBuffer, bitmap);
        }

        private void button1_Click(object sender, EventArgs e)
        {
            angle += Math.DegreeToRadian(22.5f);
        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            profiler.Reset();

            timer.Start();

            Render();

            //float current = (float) sw.Elapsed.TotalMilliseconds;
            //movingAverage += (current - movingAverage) / 10.0f;
            //label2.Text = (int) current + " ms " + (int)movingAverage + " ms";

            pictureBox1.Invalidate();

            timer.Stop();

            richTextBox1.Text = profiler.Overview();
        }

        private void panel1_Paint(object sender, PaintEventArgs e)
        {

        }
    }
}
using System;
using System.Collections.Generic;
using System.Text;

namespace Aquila
{
    public class MatrixTextureUniform
    {
        public Matrix4 matrix;
        public Texture2<Vector4> texture;

        public MatrixTextureUniform()
        {
            //
        }

        public MatrixTextureUniform(Matrix4 matrix, Texture2<Vector4> texture)
        {
            this.matrix = matrix;
            this.texture = texture;
        }
    }

    public class PositionNormalTexcoordVertex
    {
        public Vector4 position;
        public Vector3 normal;
        public Vector2 texcoord;

        public PositionNormalTexcoordVertex(Vector4 position, Vector3 normal, Vector2 texcoord)
        {
            this.position = position;
            this.normal = normal;
            this.texcoord = texcoord;
        }
    }

    public class NormalTexcoordVarying : Varying
    {
        public Vector3 normal;
        public Vector2 texcoord;

        public void Load(float[] values)
        {
            this.normal.X = values[0];
            this.normal.Y = values[1];
            this.normal.Z = values[2];
            this.texcoord.S = values[3];
            this.texcoord.T = values[4];
        }

        public void Store(float[] values)
        {
            values[0] = this.normal.X;
            values[1] = this.normal.Y;
            values[2] = this.normal.Z;
            values[3] = this.texcoord.S;
            values[4] = this.texcoord.T;
        }

        public int Elements()
        {
            return 5;
        }
    }

    public class PositionColorVertex
    {
        public Vector4 position;
        public Vector4 color;

        public PositionColorVertex(Vector4 position, Vector4 color)
        {
            this.position = position;
            this.color = color;
        }
    }

    public class ColorVarying : Varying
    {
        public Vector4 color;

        public void Load(float[] values)
        {
            this.color.R = values[0];
            this.color.G = values[1];
            this.color.B = values[2];
            this.color.A = values[3];
        }

        public void Store(float[] values)
        {
            values[0] = this.color.R;
            values[1] = this.color.G;
            values[2] = this.color.B;
            values[3] = this.color.A;
        }

        public int Elements()
        {
            return 4;
        }
    }
}

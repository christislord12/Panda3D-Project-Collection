namespace Aquila
{
    public class TextureUtility
    {
        public static void SaveToRGB(Texture2<Vector4> texture, System.Drawing.Bitmap bitmap)
        {
            int width = texture.Width;
            int height = texture.Height;

            System.Drawing.Imaging.BitmapData data = bitmap.LockBits(
                new System.Drawing.Rectangle(0, 0, width, height),
                System.Drawing.Imaging.ImageLockMode.WriteOnly,
                System.Drawing.Imaging.PixelFormat.Format24bppRgb);

            unsafe
            {
                byte* pixel = (byte*)data.Scan0;

                for (int y = 0; y < height; y++)
                {
                    for (int x = 0; x < width; x++)
                    {
                        Vector4 color = texture.GetPixel(x, y);
                        byte r = (byte)(color.R * 255);
                        byte g = (byte)(color.G * 255);
                        byte b = (byte)(color.B * 255);
                        pixel[0] = b;
                        pixel[1] = g;
                        pixel[2] = r;
                        pixel += 3;
                    }
                }
            }

            bitmap.UnlockBits(data);
        }

        public static void SaveToRGB(Texture2<Vector1> texture, System.Drawing.Bitmap bitmap)
        {
            int width = texture.Width;
            int height = texture.Height;

            System.Drawing.Imaging.BitmapData data = bitmap.LockBits(
                new System.Drawing.Rectangle(0, 0, width, height),
                System.Drawing.Imaging.ImageLockMode.WriteOnly,
                System.Drawing.Imaging.PixelFormat.Format24bppRgb);

            unsafe
            {
                byte* pixel = (byte*)data.Scan0;

                for (int y = 0; y < height; y++)
                {
                    for (int x = 0; x < width; x++)
                    {
                        float color = texture.GetPixel(x, y).X;
                        byte r = (byte)(color * 255);
                        byte g = (byte)(color * 255);
                        byte b = (byte)(color * 255);
                        pixel[0] = b;
                        pixel[1] = g;
                        pixel[2] = r;
                        pixel += 3;
                    }
                }
            }

            bitmap.UnlockBits(data);
        }

        public static void LoadFromRGB(Texture2<Vector4> texture, System.Drawing.Bitmap bitmap)
        {
            int width = bitmap.Width;
            int height = bitmap.Height;

            System.Drawing.Imaging.BitmapData data = bitmap.LockBits(
                new System.Drawing.Rectangle(0, 0, width, height),
                System.Drawing.Imaging.ImageLockMode.ReadOnly,
                System.Drawing.Imaging.PixelFormat.Format24bppRgb);

            unsafe
            {
                byte* pixel = (byte*)data.Scan0;

                for (int y = 0; y < height; y++)
                {
                    for (int x = 0; x < width; x++)
                    {
                        float b = pixel[0] / 255.0f;
                        float g = pixel[1] / 255.0f;
                        float r = pixel[2] / 255.0f;
                        pixel += 3;
                        texture.SetPixel(x, y, new Vector4(r, g, b, 1.0f));
                    }
                }
            }
        }
    }
}

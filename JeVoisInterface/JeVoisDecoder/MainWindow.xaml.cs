using System;
using System.Collections.Generic;
using System.IO.Ports;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using ExtendedSerialPort;
using System.Windows.Threading;
using System.Globalization;
using System.Collections.Concurrent;
using System.Timers;
using System.IO;
using Microsoft.Win32;
using MathNet.Numerics.LinearAlgebra;
using MathNet.Numerics;

namespace JeVoisDecoder
{
    /// <summary>
    /// Logique d'interaction pour MainWindow.xaml
    /// </summary>
    public partial class MainWindow : System.Windows.Window
    {
        ReliableSerialPort serialPort1;

        public MainWindow()
        {
            serialPort1 = new ReliableSerialPort("COM7", 460800, Parity.None, 8, StopBits.One);
            serialPort1.DataReceived += SerialPort1_DataReceived;
            serialPort1.Open();
        }

        ConcurrentQueue<byte> receivedData = new ConcurrentQueue<byte>();
        private void SerialPort1_DataReceived(object sender, DataReceivedArgs e)
        {
            foreach (var c in e.Data)
            {
                ProcessJeVoisData(c);
            }
        }

        string jeVoisCurrentFrame = "";
        List<ArucoLutElement> ArucoLut = new List<ArucoLutElement>();
        double x1, x2, x3, x4, y1, y2, y3, y4, X, Y, W, H;
        char type;

        void ProcessJeVoisData(byte c)
        {
            if (c == 'D')
            {
                type = 'D';
                AnalyzeData(jeVoisCurrentFrame,'D');
                jeVoisCurrentFrame = "";
            }
            else if(c == 'N')
            {
                type = 'N';
                AnalyzeData(jeVoisCurrentFrame, 'N');
                jeVoisCurrentFrame = "";
            }
            jeVoisCurrentFrame += Encoding.UTF8.GetString(new byte[] { c }, 0, 1);
        }

        private void Analyze_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog opfd = new OpenFileDialog();
            if (opfd.ShowDialog() == true) 
            {
                ArucoLut = new List<ArucoLutElement>();
                using (var reader = new StreamReader(opfd.FileName))
                {
                    while (!reader.EndOfStream)
                    {
                        var line = reader.ReadLine();
                        var values = line.Split(';');
                        int pos = 0;

                        ArucoLutElement lutElement = new ArucoLutElement();
                        lutElement.xField = double.Parse(values[pos++].Replace(".", ","));
                        lutElement.yField = double.Parse(values[pos++].Replace(".", ","));
                        lutElement.thetaField = double.Parse(values[pos++]);

                        if (values.Length == 11) // detail frame
                        {
                            double x = int.Parse(values[pos++]);
                            double y = int.Parse(values[pos++]);
                            lutElement.pt1 = new PointD(x, y);
                            x = int.Parse(values[pos++]);
                            y = int.Parse(values[pos++]);
                            lutElement.pt2 = new PointD(x, y);
                            x = int.Parse(values[pos++]);
                            y = int.Parse(values[pos++]);
                            lutElement.pt3 = new PointD(x, y);
                            x = int.Parse(values[pos++]);
                            y = int.Parse(values[pos++]);
                            lutElement.pt4 = new PointD(x, y);

                            lutElement.xMeasured = (lutElement.pt1.X + lutElement.pt2.X + lutElement.pt3.X + lutElement.pt4.X) / 4.0;
                            lutElement.yMeasured = (lutElement.pt1.Y + lutElement.pt2.Y + lutElement.pt3.Y + lutElement.pt4.Y) / 4.0;

                        }
                        else if (values.Length == 7) // normal frame
                        {
                            lutElement.xMeasured = int.Parse(values[pos++]);
                            lutElement.yMeasured = int.Parse(values[pos++]);
                            lutElement.W = int.Parse(values[pos++]);
                            lutElement.H = int.Parse(values[pos++]);
                            //lutElement.xMeasured += lutElement.W / 2;
                            //lutElement.yMeasured += lutElement.H / 2;
                        }

                        ArucoLut.Add(lutElement);

                        // Génération du symétrique par rapport à l'axe vertical

                        if (lutElement.xField != 0)
                        {
                            ArucoLutElement lutElementSym = new ArucoLutElement();

                            lutElementSym.xField = -lutElement.xField;
                            lutElementSym.yField = lutElement.yField;
                            lutElementSym.xMeasured = -lutElement.xMeasured;
                            lutElementSym.yMeasured = lutElement.yMeasured;
                            lutElementSym.thetaField = 180 - lutElement.thetaField;

                            ArucoLut.Add(lutElementSym);
                        }

                    }
                }
            }
        }

        // frames for normal mode : N2 id Xcenter Ycenter W H
        // frames for detail mode [YOLO] : D2 id x1 y1 x2 y2 x3 y3 x4 y4
        // frames for detail mode [ArUco] : D2 id nb_pts x1 y1 x2 y2 x3 y3 x4 y4
        // for DNN, id = name:%confidence
        // http://jevois.org/doc/UserSerialStyle.html
        
        
        double xMeasured = 0, yMeasured = 0;
        private void AnalyzeData(string s, char type)
        {
            string outputString = "";
            string[] inputArray = s.Split(' ');
            for (int i = 0; i < inputArray.Length; i++)
            {
                inputArray[i] = inputArray[i].Replace('.', ',');
            }


            switch (type)
            {
                case 'D':
                    if (inputArray.Length == 10) // Yolo darknet dnn size = 10 | c++ aruco detector size = 11
                    {
                        string ID = inputArray[1];
                        x1 = double.Parse(inputArray[2]);
                        y1 = double.Parse(inputArray[3]);
                        x2 = double.Parse(inputArray[4]);
                        y2 = double.Parse(inputArray[5]);
                        x3 = double.Parse(inputArray[6]);
                        y3 = double.Parse(inputArray[7]);
                        x4 = double.Parse(inputArray[8]);
                        y4 = double.Parse(inputArray[9]);

                        xMeasured = (x1 + x2 + x3 + x4) / 4.0;
                        yMeasured = (y1 + y2 + y3 + y4) / 4.0;
                    }
                    else
                    {
                        Console.WriteLine("size error for detail frame - frame size = " + inputArray.Length);
                        return;
                    }
                    break;

                case 'N':
                    if (inputArray.Length == 6)
                    {
                        string[] ID = inputArray[1].Split(':');
                        string name = ID[0];
                        string percent = ID[1];

                        ///Centre 0;0 au centre de l'image
                        ///Negatif en X à Gauche
                        ///Negatif en Y en haut
                        /// La Jevois revoie des coordonnées pourries
                        /// On récupère en premier le point haut gauche de la Bouding Box
                        /// Et ensuite, la largeur et hauteur
                        /// Tout est en pixels

                        var XHg = double.Parse(inputArray[2]);
                        var YHg = double.Parse(inputArray[3]);
                        W = double.Parse(inputArray[4]);
                        H = double.Parse(inputArray[5]);

                        xMeasured = XHg+W/2;
                        yMeasured = YHg+H/2;

                        outputString = name + " - Confidence : " + percent + " - Center X : " + xMeasured.ToString("N1") + " - Y : " + yMeasured.ToString("N1");
                        Console.WriteLine(outputString);
                    }
                    else
                    {
                        Console.WriteLine("size error for normal frame - frame size = " + inputArray.Length);
                        return;
                    }
                    break;

            }

            if (ArucoLut.Count > 0)
            {
                // On calcule la distance à chaque element de la LUT
                var ArucoClosestList = ArucoLut.OrderBy(p => Math.Sqrt(Math.Pow(xMeasured - p.xMeasured, 2) + Math.Pow(yMeasured - p.yMeasured, 2))).ToList();

                var closestPoint = ArucoClosestList[0];
                var closestPoint2 = ArucoClosestList[1];
                ArucoLutElement closestPoint3 = ArucoClosestList[2];

                //Console.WriteLine(String.Format("Real : ({0},{1}) | Clos1 : ({2},{3}) | Clos2 : ({4},{5}) | Clos3 : ({6},{7})", 
                //    xMeasured,yMeasured,closestPoint.xMeasured,closestPoint.yMeasured,closestPoint2.xMeasured,
                //    closestPoint2.yMeasured,closestPoint3.xMeasured,closestPoint3.yMeasured));

                double vectorielProduct;
                int pos = 2;
                do
                {
                    closestPoint3 = ArucoClosestList[pos];
                    pos++;
                    var V12field = Vector<double>.Build.DenseOfArray(new double[] {
                                    closestPoint.xField - closestPoint2.xField,
                                    closestPoint.yField - closestPoint2.yField });

                    var V13field = Vector<double>.Build.DenseOfArray(new double[] {
                                    closestPoint.xField - closestPoint3.xField,
                                    closestPoint.yField - closestPoint3.yField });
                    vectorielProduct = (double)AlgebraTools.Cross(V12field, V13field);
                }
                while (vectorielProduct == 0); // On ne garde pas le 3e pt si les 3 sont alignés

                // On calcule le gradient de distance mesurée entre le pt le plus proche et le 2e pt le plus proche
                PointD gradient12 = new PointD(
                    closestPoint.xMeasured - closestPoint2.xMeasured,
                    closestPoint.yMeasured - closestPoint2.yMeasured);

                // On calcule le gradient de distance mesurée entre le pt le plus proche et le 3e pt le plus proche
                PointD gradient13 = new PointD(
                    closestPoint.xMeasured - closestPoint3.xMeasured,
                    closestPoint.yMeasured - closestPoint3.yMeasured);

                // On calcule l'écart entre le pt le plus proche et le pt détecté
                PointD ecartClosestPoint = new PointD(
                    closestPoint.xMeasured - xMeasured,
                    closestPoint.yMeasured - yMeasured);

                // On détermine les coeff a et b tq : ecartClosestPoint = a * gradient12 + b * gradient13
                var M = CreateMatrix.Dense(2, 2, new double[] { gradient12.X, gradient12.Y, gradient13.X, gradient13.Y });
                var MInv = M.Inverse();

                Vector<double> v = Vector<double>.Build.DenseOfArray(new double[] { ecartClosestPoint.X, ecartClosestPoint.Y });

                var ab = MInv.Multiply(v);

                // On calcule les coordonnées du pt mesuré dans le terrain
                PointD posArucoField = new PointD(
                    closestPoint.xField - ab[0] * (closestPoint.xField - closestPoint2.xField) - ab[1] * (closestPoint.xField - closestPoint3.xField),
                    closestPoint.yField - ab[0] * (closestPoint.yField - closestPoint2.yField) - ab[1] * (closestPoint.yField - closestPoint3.yField));

                //Console.WriteLine("Pos calculée : " + posArucoField.X.ToString("F1") + " | " + posArucoField.Y.ToString("F1"));
                Console.WriteLine(String.Format("Current center : ({0};{1}) |  Pos calculée : ({2};{3})",
                    xMeasured, yMeasured, posArucoField.X.ToString("F1"), posArucoField.Y.ToString("F1")));
            }
            else
            {
                //Console.WriteLine(s);
            }
        }

        private void button_Click(object sender, RoutedEventArgs e)
        {

            //string path = "C:\\GitHub\\Stage-GEII\\JeVoisInterface\\Data\\log.csv";
            string path = filePath.Text;

            string Xreel = tbXreel.Text;
            string Yreel = tbYreel.Text;
            string Theta = tbTheta.Text;

            tbXreel.Text = ""; tbYreel.Text = ""; tbTheta.Text = "0";

            
            string log = "";

            switch(type)
            {
                case 'D':
                    log = Xreel + ";" + Yreel + ";" + Theta + ";" + x1 + ";" + y1 + ";" + x2 + ";" + y2 + ";" + x3 + ";" + y3 + ";" + x4 + ";" + y4;
                    break;
                case 'N':
                    double Xcalculated = xMeasured;
                    double Ycalculated = yMeasured;
                    log = Xreel + ";" + Yreel + ";" + Theta + ";" + Xcalculated.ToString("N0") + ";" + Ycalculated.ToString("N0") + ";" + W + ";" + H;
                    break;
            }

            using (StreamWriter file = new StreamWriter(path, append: true))
            {
                file.WriteLine(log);
            }
        }
    }

    public class ArucoLutElement
    {
        public double xField;
        public double yField;
        public double thetaField;
        public double xMeasured;
        public double yMeasured;
        public double W;
        public double H;
        public PointD pt1;
        public PointD pt2;
        public PointD pt3;
        public PointD pt4;
    }

    public class PointD
    {
        public double X;
        public double Y;
        public PointD(double x, double y)
        {
            X = x;
            Y = y;
        }
    }

    public static class AlgebraTools
    {
        public static double? Cross(Vector<double> left, Vector<double> right)
        {
            double? result = null;
            if ((left.Count == 2 && right.Count == 2))
            {
                result = left[0] * right[1] - left[1] * right[0];
            }

            return result;
        }
    }
}

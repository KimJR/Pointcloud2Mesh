
import pymesh;

mesh = pymesh.load_mesh("MyObject.obj"); #the object should include an array of all faces (triangles), with each triangle including an array of 3 vertices
colorMap = texture #the texture to which the color will be mapped
normalMap = texture #the texture to which the normal color will be mapped
positionMap = texture #the texture to which the position of the vertices will be mapped

for t in mesh.faces:
	#get vertex UVs
	x1 = t.vertex[0].u
	y1 = t.vertex[0].v
	x2 = t.vertex[1].u
	y2 = t.vertex[1].v
	x3 = t.vertex[2].u
	y3 = t.vertex[2].v

    #get smallest square of pixels that includes all three vertex uv positions
    sqxStart = min(x1, x2, x3)
    sqxEnd = max(x1, x2, x3)
    sqyStart = min(y1, y2, y3)
    sqyEnd = max(y1, y2, y3)

    #cycle through each pixel within the square to see if the pixel is within the triangle
    for y in range (sqyStart*colorTexture.width, sqyEnd*colorTexture.width):
        for x in range (sqyStart*colorTexture.width, sqyEnd*colorTexture.width):
	        
            #get factors a, b, c such that 
            #x = a * x1 + b * x2  + c * x3
            #y = a * y1 + b * y2 + c * y3
            #a + b + c = 1
            a = ((y2 - y3)*(x - x3) + (x3 - x2)*(y - y3)) / ((y2 - y3)*(x1 - x3) + (x3 - x2)*(y1 - y3))
            b = ((y3 - y1)*(x - x3) + (x1 - x3)*(y - y3)) / ((y2 - y3)*(x1 - x3) + (x3 - x2)*(y1 - y3))
            c = 1 - a - b

            #check if point is within triangle
            if 0 <= a & a <= 1 & 0 <= b & b <= 1 & 0 <= c & c <= 1:

	            #color the pixel depending on the lerp between the three pixels
	            pixelColor = a*t.vertex[0].color + b*t.vertex[1].color + c*t.vertex[2].color
	            colorMap.SetPixel(int(x*colorTexture.width), int(y*colorTexture.width), pixelColor)

                pixelNormalColor = (a*t.vertex[0].normal + b*t.vertex[1].normal + c*t.vertex[2].normal)/2 + vector3(0.5,0.5,0.5)
                normalMap.SetPixel(int(x*colorTexture.width), int(y*colorTexture.width), pixelNormalColor)

                pixelPositionColor = (a*t.vertex[0].position + b*t.vertex[1].position + c*t.vertex[2].position)
                positionMap.SetPixel(int(x*colorTexture.width), int(y*colorTexture.width), pixelPositionColor)
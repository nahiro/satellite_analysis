from osgeo import gdal
import numpy as np

pi2 = 2.0*np.pi
pi_2 = np.pi/2

def getang(x1,y1,x2,y2):
    ang = np.arccos(np.clip((x1*x2+y1*y2)/(np.sqrt(x1*x1+y1*y1)*np.sqrt(x2*x2+y2*y2)),-1.0,1.0))
    zp = x1*y2-y1*x2
    if np.iterable(x1) or np.iterable(x2):
        cnd = (zp < 0.0) # clockwise
        ang[cnd] *= -1.0
        ang[cnd] += pi2
    else:
        if zp < 0.0: # clockwise
            ang = pi2-ang
    return ang

def freeman_chain():
    sqr2 = np.sqrt(2.0)
    c_code = [(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1),(1,1),
              (1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1),(1,1)] # dx,dy
    l_code = [np.sqrt(dx*dx+dy*dy) for dx,dy in c_code]
    next_code = [7,7,1,1,3,3,5,5,
                 7,7,1,1,3,3,5,5]
    return

EPSILON = 1.0e-6

ds = gdal.Open('parcel_mask.tif')
src_nx = ds.RasterXSize
src_ny = ds.RasterYSize
src_nb = ds.RasterCount
src_shape = (src_ny,src_nx)
src_prj = ds.GetProjection()
src_trans = ds.GetGeoTransform()
src_meta = ds.GetMetadata()
src_data = ds.ReadAsArray().reshape(src_ny,src_nx)
src_indy,src_indx = np.indices(src_shape)
src_xmin = src_trans[0]
src_xstp = src_trans[1]
src_xmax = src_xmin+src_nx*src_xstp
src_ymax = src_trans[3]
src_ystp = src_trans[5]
src_ymin = src_ymax+src_ny*src_ystp
src_xp = src_xmin+(src_indx+0.5)*src_xstp+(src_indy+0.5)*src_trans[2]
src_yp = src_ymax+(src_indy+0.5)*src_ystp+(src_indx+0.5)*src_trans[4]
ds = None
cnd = (src_data > 0.5)
xcnd = src_xp[cnd]
ycnd = src_yp[cnd]
fcnd = np.full(xcnd.shape,True)

ymax = ycnd.max()
cnd2 = (np.abs(ycnd-ymax) < EPSILON)
xc = xcnd[cnd2]
yc = ycnd[cnd2]
if xc.size > 1:
    indx = np.argmin(xc)
    x0 = xc[indx]
    y0 = yc[indx]
else:
    x0 = xc[0]
    y0 = yc[0]

l = 100.0 # m
ll = l*l
a1 = -1.0
b1 = 1.0
x1 = x0
y1 = y0
x2 = np.nan
y2 = np.nan
xs = [x1]
ys = [y1]
while (x2,y2) != (x0,y0):
    dx = xcnd-x1
    dy = ycnd-y1
    r2 = np.square(dx)+np.square(dy)
    cnd2 = (r2 > 0.0) & (r2 < ll) & fcnd
    xc = xcnd[cnd2]
    yc = ycnd[cnd2]
    if xc.size < 1:
        raise ValueError('Error in finding adjacent pixels.')
    elif xc.size > 1:
        dxcnd = dx[cnd2]
        dycnd = dy[cnd2]
        ang = getang(a1,b1,dxcnd,dycnd)
        ang[ang < pi_2] = pi2
        amin = ang.min()
        cnd3 = (np.abs(ang-amin) < EPSILON)
        xc2 = xc[cnd3]
        yc2 = yc[cnd3]
        if xc2.size > 1:
            rc = r2[cnd2]
            rc2 = rc[cnd3]
            indx = np.argmin(rc2)
            x2 = xc2[indx]
            y2 = yc2[indx]
        else:
            x2 = xc2[0]
            y2 = yc2[0]
    else:
        x2 = xc[0]
        y2 = yc[0]
    #if len(xs) > 5:
    #    break
    cnd4 = (xcnd == x1) & (ycnd == y1) & (xcnd != x0)
    fcnd[cnd4] = False
    a1 = x1-x2
    b1 = y1-y2
    x1 = x2
    y1 = y2
    xs.append(x2)
    ys.append(y2)

try:
    import gdal
except Exception:
    from osgeo import gdal
from shapely.geometry import Polygon
import numpy as np
import geopandas as gpd
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
PI2 = 2.0*np.pi
PI_4 = np.pi/4
EPSILON = 1.0e-6

# Default values
EPSG = 32748 # UTM zone 48S
LMIN = 50.0 # m
LMAX = 500.0 # m
LSTP = 50.0 # m

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%(default)s)')
parser.add_argument('-o','--out_shp',default=None,help='Output Shapefile name (%(default)s)')
parser.add_argument('-E','--epsg',default=EPSG,help='Output EPSG (%(default)s)')
parser.add_argument('-l','--lmin',default=LMIN,type=float,help='Minimum arm length in m (%(default)s)')
parser.add_argument('-L','--lmax',default=LMAX,type=float,help='Maximum arm length in m (%(default)s)')
parser.add_argument('-s','--lstp',default=LSTP,type=float,help='Step arm length in m (%(default)s)')
parser.add_argument('-F','--fignam',default=None,help='Output figure name for debug (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()

def getang(x1,y1,x2,y2):
    ang = np.arccos(np.clip((x1*x2+y1*y2)/(np.sqrt(x1*x1+y1*y1)*np.sqrt(x2*x2+y2*y2)),-1.0,1.0))
    zp = x1*y2-y1*x2
    if np.iterable(x1) or np.iterable(x2):
        cnd = (zp < 0.0) # clockwise
        ang[cnd] *= -1.0
        ang[cnd] += PI2
    else:
        if zp < 0.0: # clockwise
            ang = PI2-ang
    return ang

def is_cross(x_a,y_a,x_b,y_b,x_c,y_c,x_d,y_d):
    if np.iterable(x_a): # x_a, y_a, x_b, y_b ... array-like
        x1 = x_a.copy()
        x2 = x_b.copy()
        cnd = (x_a > x_b)
        x1[cnd] = x_b[cnd]
        x2[cnd] = x_a[cnd]
        y1 = y_a.copy()
        y2 = y_b.copy()
        cnd = (y_a > y_b)
        y1[cnd] = y_b[cnd]
        y2[cnd] = y_a[cnd]
    else: # x_a, y_a, x_b, y_b ... scalar
        x1,x2 = (x_b,x_a) if x_a > x_b else (x_a,x_b)
        y1,y2 = (y_b,y_a) if y_a > y_b else (y_a,y_b)
    if np.iterable(x_c): # x_c, y_c, x_d, y_d ... array-like
        x3 = x_c.copy()
        x4 = x_d.copy()
        cnd = (x_c > x_d)
        x3[cnd] = x_d[cnd]
        x4[cnd] = x_c[cnd]
        y3 = y_c.copy()
        y4 = y_d.copy()
        cnd = (y_c > y_d)
        y3[cnd] = y_d[cnd]
        y4[cnd] = y_c[cnd]
    else:
        x3,x4 = (x_d,x_c) if x_c > x_d else (x_c,x_d)
        y3,y4 = (y_d,y_c) if y_c > y_d else (y_c,y_d)
    if np.iterable(x_a) or np.iterable(x_c):
        flag = ~((x3 > x2) | (x4 < x1) | (y3 > y2) | (y4 < y1))
        if np.iterable(x_a):
            x_a_f = x_a[flag]
            x_b_f = x_b[flag]
            y_a_f = y_a[flag]
            y_b_f = y_b[flag]
        else:
            x_a_f = x_a
            x_b_f = x_b
            y_a_f = y_a
            y_b_f = y_b
        if np.iterable(x_c):
            x_c_f = x_c[flag]
            x_d_f = x_d[flag]
            y_c_f = y_c[flag]
            y_d_f = y_d[flag]
        else:
            x_c_f = x_c
            x_d_f = x_d
            y_c_f = y_c
            y_d_f = y_d
        s = (x_a_f-x_b_f)*(y_c_f-y_a_f)-(y_a_f-y_b_f)*(x_c_f-x_a_f)
        t = (x_a_f-x_b_f)*(y_d_f-y_a_f)-(y_a_f-y_b_f)*(x_d_f-x_a_f)
        cnd = ~(s*t > EPSILON)
        s = (x_c_f-x_d_f)*(y_a_f-y_c_f)-(y_c_f-y_d_f)*(x_a_f-x_c_f)
        t = (x_c_f-x_d_f)*(y_b_f-y_c_f)-(y_c_f-y_d_f)*(x_b_f-x_c_f)
        cnd &= (~(s*t > EPSILON))
        flag[flag] = cnd
        return flag
    else:
        if (x3 > x2) or (x4 < x1) or (y3 > y2) or (y4 < y1):
            return False
        s = (x_a-x_b)*(y_c-y_a)-(y_a-y_b)*(x_c-x_a)
        t = (x_a-x_b)*(y_d-y_a)-(y_a-y_b)*(x_d-x_a)
        if (s*t > EPSILON):
            return False
        s = (x_c-x_d)*(y_a-y_c)-(y_c-y_d)*(x_a-x_c)
        t = (x_c-x_d)*(y_b-y_c)-(y_c-y_d)*(x_b-x_c)
        if (s*t > EPSILON):
            return False
        return True

def freeman_chain(im,ix1,iy1,ix2,iy2,ic):
    c_code = [(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1),(1,1),
              (1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1),(1,1)] # dx,dy
    l_code = [np.sqrt(dx*dx+dy*dy) for dx,dy in c_code]
    next_code = [7,7,1,1,3,3,5,5,
                 7,7,1,1,3,3,5,5]
    ix_1 = ix1
    iy_1 = iy1
    xy = [(ix1,iy1)]
    i_code = ic
    lmax = np.sqrt(np.square(ix2-ix1)+np.square(iy2-iy1))*2.0
    lsum = 0.0
    while True:
        flag = False
        for i in range(i_code,i_code+8):
            ix_2 = ix_1+c_code[i][0]
            iy_2 = iy_1+c_code[i][1]
            if im[iy_2,ix_2]:
                flag = True
                lsum += l_code[i]
                break
        if not flag:
            #raise ValueError('Error in freeman chain')
            return None
        elif lsum > lmax:
            return None
        elif (ix_2,iy_2) == (ix2,iy2):
            break
        elif ((ix_2,iy_2)) in xy:
            return None
        else:
            xy.append((ix_2,iy_2))
            ix_1 = ix_2
            iy_1 = iy_2
            i_code = next_code[i]
    return xy

ds = gdal.Open(args.src_geotiff)
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
img = (src_data > 0.5)
xcnd = src_xp[img]
ycnd = src_yp[img]

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

a1 = -1.0
b1 = 1.0
x1 = x0
y1 = y0
x2 = np.nan
y2 = np.nan
xs = np.array([x1])
ys = np.array([y1])
xxs = []
yys = []
while (x2,y2) != (x0,y0):
    dx = xcnd-x1
    dy = ycnd-y1
    r2 = np.square(dx)+np.square(dy)
    flag = False
    for l in np.arange(args.lmin,args.lmax+0.1*args.lstp,args.lstp):
        ll = l*l
        cnd2 = (r2 > EPSILON) & (r2 < ll)
        xc = xcnd[cnd2]
        yc = ycnd[cnd2]
        if xc.size < 1:
            continue
        elif xc.size > 1:
            dxcnd = dx[cnd2]
            dycnd = dy[cnd2]
            ang = getang(a1,b1,dxcnd,dycnd)
            ang[ang < EPSILON] = PI2
            a_inds = np.argsort(ang)
            amin = ang[a_inds[0]]
            if amin > np.pi*0.08: # Outside
                cnd3 = (np.abs(ang-amin) < EPSILON)
                xc2 = xc[cnd3]
                yc2 = yc[cnd3]
                if xc2.size > 1:
                    rc = r2[cnd2]
                    rc2 = rc[cnd3]
                    r_indx = np.argmin(rc2)
                    x2 = xc2[r_indx]
                    y2 = yc2[r_indx]
                else:
                    x2 = xc2[0]
                    y2 = yc2[0]
                if len(xs) < 3:
                    flag = True
                elif not np.any(is_cross(xs[:-2],ys[:-2],xs[1:-1],ys[1:-1],x1,y1,x2,y2)) or (x2,y2) == (x0,y0):
                    flag = True
            else: # Inside
                for a_indx in a_inds:
                    amin = ang[a_indx]
                    cnd3 = (np.abs(ang-amin) < EPSILON)
                    xc2 = xc[cnd3]
                    yc2 = yc[cnd3]
                    if xc2.size > 1:
                        rc = r2[cnd2]
                        rc2 = rc[cnd3]
                        r_indx = np.argmin(rc2)
                        x2 = xc2[r_indx]
                        y2 = yc2[r_indx]
                    else:
                        x2 = xc2[0]
                        y2 = yc2[0]
                    if len(xs) < 3:
                        flag = True
                        break
                    elif not np.any(is_cross(xs[:-2],ys[:-2],xs[1:-1],ys[1:-1],x1,y1,x2,y2)) or (x2,y2) == (x0,y0):
                        flag = True
                        break
                    else:
                        ang[a_indx] = PI2
        else:
            x2 = xc[0]
            y2 = yc[0]
            if len(xs) < 3:
                flag = True
            elif not np.any(is_cross(xs[:-2],ys[:-2],xs[1:-1],ys[1:-1],x1,y1,x2,y2)):
                flag = True
        if flag:
            break
    if not flag:
        raise ValueError('Error in finding end point.')
    #if len(xs) > 4426:
    #    break
    xy = freeman_chain(img,int((x1-src_xmin)/src_xstp),int((y1-src_ymax)/src_ystp),int((x2-src_xmin)/src_xstp),int((y2-src_ymax)/src_ystp),np.mod(int(np.arctan2(y2-y1,x2-x1)/PI_4-EPSILON)+1,8))
    if xy is None:
        xxs.append(x1)
        yys.append(y1)
    else:
        xxs.extend([src_xp[iy,ix] for ix,iy in xy[:-1]])
        yys.extend([src_yp[iy,ix] for ix,iy in xy[:-1]])
    a1 = x1-x2
    b1 = y1-y2
    x1 = x2
    y1 = y2
    xs = np.append(xs,x2)
    ys = np.append(ys,y2)

polygon_geom = Polygon(zip(xs,ys))
polygon = gpd.GeoDataFrame(index=[0],crs='epsg:{}'.format(args.epsg),geometry=[polygon_geom])
polygon.to_file(filename=args.out_shp,driver="ESRI Shapefile")

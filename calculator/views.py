import json
import math
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


def index(request):
    return render(request, 'calculator/index.html')


@csrf_exempt
@require_http_methods(["POST"])
def calculate(request):
    try:
        data = json.loads(request.body)
        motion_type = data.get('type')
        params = data.get('params', {})

        if motion_type == 'mru':
            result = calc_mru(params)
        elif motion_type == 'mruv':
            result = calc_mruv(params)
        elif motion_type == 'mc':
            result = calc_mc(params)
        elif motion_type == 'caida_libre':
            result = calc_caida_libre(params)
        elif motion_type == 'tiro_vertical':
            result = calc_tiro_vertical(params)
        elif motion_type == 'parabolico':
            result = calc_parabolico(params)
        else:
            return JsonResponse({'error': 'Tipo de movimiento desconocido'}, status=400)

        return JsonResponse({'success': True, 'data': result})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def calc_mru(p):
    """Movimiento Rectilíneo Uniforme: x = x0 + v*t"""
    v = float(p.get('v', 10))       # velocidad m/s
    x0 = float(p.get('x0', 0))      # posición inicial m
    t_max = float(p.get('t_max', 10))  # tiempo máximo s

    steps = 200
    dt = t_max / steps
    times, positions, velocities = [], [], []

    for i in range(steps + 1):
        t = i * dt
        x = x0 + v * t
        times.append(round(t, 4))
        positions.append(round(x, 4))
        velocities.append(round(v, 4))

    return {
        'times': times,
        'positions': positions,
        'velocities': velocities,
        'accelerations': [0.0] * len(times),
        'summary': {
            'Velocidad': f'{v} m/s',
            'Posición inicial': f'{x0} m',
            'Posición final': f'{round(x0 + v * t_max, 2)} m',
            'Tiempo total': f'{t_max} s',
            'Distancia recorrida': f'{round(abs(v * t_max), 2)} m',
        }
    }


def calc_mruv(p):
    """Movimiento Rectilíneo Uniformemente Variado: x = x0 + v0*t + ½*a*t²"""
    v0 = float(p.get('v0', 0))
    a = float(p.get('a', 2))
    x0 = float(p.get('x0', 0))
    t_max = float(p.get('t_max', 10))

    steps = 200
    dt = t_max / steps
    times, positions, velocities, accelerations = [], [], [], []

    for i in range(steps + 1):
        t = i * dt
        x = x0 + v0 * t + 0.5 * a * t ** 2
        v = v0 + a * t
        times.append(round(t, 4))
        positions.append(round(x, 4))
        velocities.append(round(v, 4))
        accelerations.append(round(a, 4))

    # tiempo de parada si decelera
    t_stop = None
    if a != 0 and (v0 / a) < 0:
        t_stop = -v0 / a

    return {
        'times': times,
        'positions': positions,
        'velocities': velocities,
        'accelerations': accelerations,
        'summary': {
            'Velocidad inicial': f'{v0} m/s',
            'Aceleración': f'{a} m/s²',
            'Posición inicial': f'{x0} m',
            'Velocidad final': f'{round(v0 + a * t_max, 2)} m/s',
            'Posición final': f'{round(x0 + v0 * t_max + 0.5 * a * t_max**2, 2)} m',
        }
    }


def calc_mc(p):
    """Movimiento Circular: θ = ω*t, v = ω*r"""
    r = float(p.get('r', 5))        # radio m
    omega = float(p.get('omega', 1))  # velocidad angular rad/s
    t_max = float(p.get('t_max', 10))
    vueltas = omega * t_max / (2 * math.pi)

    steps = 400
    dt = t_max / steps
    times, angles, vt_list, ac_list = [], [], [], []
    x_pos, y_pos = [], []

    for i in range(steps + 1):
        t = i * dt
        theta = omega * t
        vt = omega * r
        ac = (omega ** 2) * r
        times.append(round(t, 4))
        angles.append(round(math.degrees(theta) % 360, 4))
        vt_list.append(round(vt, 4))
        ac_list.append(round(ac, 4))
        x_pos.append(round(r * math.cos(theta), 4))
        y_pos.append(round(r * math.sin(theta), 4))

    periodo = 2 * math.pi / omega if omega != 0 else 0
    frecuencia = 1 / periodo if periodo != 0 else 0

    return {
        'times': times,
        'angles': angles,
        'velocities': vt_list,
        'accelerations': ac_list,
        'x_pos': x_pos,
        'y_pos': y_pos,
        'summary': {
            'Radio': f'{r} m',
            'Vel. angular (ω)': f'{omega} rad/s',
            'Vel. tangencial': f'{round(omega * r, 2)} m/s',
            'Ac. centrípeta': f'{round(omega**2 * r, 2)} m/s²',
            'Período': f'{round(periodo, 3)} s',
            'Frecuencia': f'{round(frecuencia, 3)} Hz',
            'Vueltas': f'{round(vueltas, 2)}',
        }
    }


def calc_caida_libre(p):
    """Caída Libre: y = h - ½*g*t²"""
    h = float(p.get('h', 50))    # altura inicial m
    g = float(p.get('g', 9.81))  # gravedad m/s²

    t_total = math.sqrt(2 * h / g) if h > 0 else 1
    steps = 200
    dt = t_total / steps
    times, heights, velocities, accelerations = [], [], [], []

    for i in range(steps + 1):
        t = i * dt
        y = h - 0.5 * g * t ** 2
        v = g * t
        if y < 0:
            y = 0
        times.append(round(t, 4))
        heights.append(round(y, 4))
        velocities.append(round(v, 4))
        accelerations.append(round(g, 4))

    v_impacto = math.sqrt(2 * g * h)

    return {
        'times': times,
        'positions': heights,
        'velocities': velocities,
        'accelerations': accelerations,
        'summary': {
            'Altura inicial': f'{h} m',
            'Gravedad': f'{g} m/s²',
            'Tiempo de caída': f'{round(t_total, 3)} s',
            'Velocidad de impacto': f'{round(v_impacto, 2)} m/s',
        }
    }


def calc_tiro_vertical(p):
    """Tiro Vertical: y = v0*t - ½*g*t²"""
    v0 = float(p.get('v0', 30))
    g = float(p.get('g', 9.81))
    y0 = float(p.get('y0', 0))

    t_subida = v0 / g
    t_total = 2 * t_subida + math.sqrt(2 * y0 / g) if y0 > 0 else 2 * t_subida
    # tiempo hasta tocar suelo
    disc = v0**2 + 2 * g * y0
    if disc >= 0:
        t_total = (v0 + math.sqrt(disc)) / g
    else:
        t_total = 2 * t_subida

    steps = 300
    dt = t_total / steps
    times, heights, velocities, accelerations = [], [], [], []

    for i in range(steps + 1):
        t = i * dt
        y = y0 + v0 * t - 0.5 * g * t ** 2
        v = v0 - g * t
        if y < 0:
            y = 0
        times.append(round(t, 4))
        heights.append(round(y, 4))
        velocities.append(round(v, 4))
        accelerations.append(round(-g, 4))

    h_max = y0 + (v0 ** 2) / (2 * g)

    return {
        'times': times,
        'positions': heights,
        'velocities': velocities,
        'accelerations': accelerations,
        'summary': {
            'Velocidad inicial': f'{v0} m/s',
            'Altura inicial': f'{y0} m',
            'Gravedad': f'{g} m/s²',
            'Altura máxima': f'{round(h_max, 2)} m',
            'Tiempo al máximo': f'{round(t_subida, 3)} s',
            'Tiempo total': f'{round(t_total, 3)} s',
        }
    }


def calc_parabolico(p):
    """Tiro Parabólico"""
    v0 = float(p.get('v0', 30))
    angle_deg = float(p.get('angle', 45))
    g = float(p.get('g', 9.81))
    y0 = float(p.get('y0', 0))

    angle_rad = math.radians(angle_deg)
    v0x = v0 * math.cos(angle_rad)
    v0y = v0 * math.sin(angle_rad)

    # tiempo de vuelo
    disc = v0y**2 + 2 * g * y0
    if disc >= 0:
        t_total = (v0y + math.sqrt(disc)) / g
    else:
        t_total = 2 * v0y / g

    steps = 300
    dt = t_total / steps
    times = []
    x_pos, y_pos = [], []
    vx_list, vy_list, v_list = [], [], []
    accelerations = []

    for i in range(steps + 1):
        t = i * dt
        x = v0x * t
        y = y0 + v0y * t - 0.5 * g * t ** 2
        vx = v0x
        vy = v0y - g * t
        speed = math.sqrt(vx**2 + vy**2)
        if y < 0:
            y = 0
        times.append(round(t, 4))
        x_pos.append(round(x, 4))
        y_pos.append(round(y, 4))
        vx_list.append(round(vx, 4))
        vy_list.append(round(vy, 4))
        v_list.append(round(speed, 4))
        accelerations.append(round(g, 4))

    h_max = y0 + (v0y ** 2) / (2 * g)
    alcance = v0x * t_total

    return {
        'times': times,
        'x_pos': x_pos,
        'y_pos': y_pos,
        'velocities': v_list,
        'vx': vx_list,
        'vy': vy_list,
        'accelerations': accelerations,
        'summary': {
            'Velocidad inicial': f'{v0} m/s',
            'Ángulo': f'{angle_deg}°',
            'V. horizontal (vx)': f'{round(v0x, 2)} m/s',
            'V. vertical (vy)': f'{round(v0y, 2)} m/s',
            'Altura máxima': f'{round(h_max, 2)} m',
            'Alcance': f'{round(alcance, 2)} m',
            'Tiempo de vuelo': f'{round(t_total, 3)} s',
        }
    }

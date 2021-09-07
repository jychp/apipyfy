import re
from multiprocessing import Process
import logging

import pyduktape

logger = logging.getLogger('apipyfy-zoomeye')


class FakeWindow:
    def __init__(self):
        self.log = []

    @property
    def _phantom(self):
        self.log.append('window._phantom')
        return None

    @property
    def __phantomas(self, **kwargs):
        self.log.append('window._phantomas')
        return None

    @property
    def callPhantom(self, **kwargs):
        self.log.append('window.callPhantom')
        return None


class ZoomEyeJs(Process):
    """
    Classe permettant de bypass le JS anti robot de ZoomEye
    """
    def __init__(self, content, result):
        Process.__init__(self)
        self.result = result
        # Extract var
        content = content.split('</script>')[0] + '</script>'
        regex = re.compile(r"var x=\"(.*)\"\.replace.*,y=\"(.*)\",f=func")
        r = regex.findall(content)
        self.x = r[0][0].split('@')
        self.y = r[0][1]
        # Iterator
        self.pos = 0
        # values
        self.timestamp = ''
        self.expired = ''

    def run(self):
        js_func = self.loop()
        if js_func is None:
            return None
        # Build JS
        STUB = '''
        var pdterror;
        try {
          var f=''' + js_func + ''';
          f();
        }
        catch(error) {
          pdterror='Pyduketape: ' + error;
          print(error.stack);
        }
        '''
        context = pyduktape.DuktapeContext()
        context.set_globals(window=FakeWindow())
        token = context.eval_js(STUB)
        error = context.get_global('pdterror')
        if error is not None:
            logger.error(f"ZoomEyeJS: {js_func})")
        if token is None:
            return None
        full_token = '{0}|0|{1}'.format(self.timestamp, token)
        self.result.append(full_token)

    def extract(self, y):
        regex = re.compile(r"document\.cookie='__cdn_clearance=(\d+\.\d+)\|(_\w+)\|\'\+\((.*)\)\(\)\+';Expires=(.*);Path")
        m = regex.findall(y)
        if len(m) == 0:
            return None
        self.timestamp = m[0][0]
        var_name = m[0][1]
        pattern = re.compile("({0})([^\da-zA-Z])".format(var_name))
        js_func = pattern.sub(r"0\2", m[0][2])
        self.expired = m[0][3]
        # Bypass navigator elements
        re1 = re.compile(r"var (\w+)=\w+.match\(.*\)\[0\];")
        re2 = re.compile(r"(\w+)=_\w+.firstChild.href")
        re3 = re.compile(
            r"var _\w+=document.createElement\('div'\);_\w+.innerHTML='.*';_\w+=_\w+.firstChild.href;var \w+=\w+.match\(.*\)\[0\];")
        replacement = ''
        elements = re1.findall(js_func)
        if len(elements) == 0:
            return js_func
        replacement += "var {0}='';".format(elements[0])
        elements = re2.findall(js_func)
        if len(elements) == 0:
            return js_func
        replacement += "var {0}='www.zoomeye.org';".format(elements[0])
        js_func = re3.sub(replacement, js_func)
        return js_func

    def z(self):
        """
        var z = f(y.match(/\w/g).sort(function(x, y) {
            return f(x) - f(y)
        }).pop());
        """
        # Split
        regex = re.compile(r"\w")
        elements = regex.findall(self.y)
        keep_e = elements[0]
        for e in elements:
            if self.f(keep_e) <= self.f(e):
                keep_e = e
        return self.f(keep_e)

    @staticmethod
    def f(x, y=False):
        """
        var f = function(x, y) {
            var a = 0,
                b = 0,
                c = 0;
            x = x.split("");
            y = y || 99;
            while ((a = x.shift()) && (b = a.charCodeAt(0) - 77.5)) c = (Math.abs(b) < 13 ? (b + 48.5) : parseInt(a, 36)) + y * c;
            return c
        }
        """
        c = 0
        if not y:
            y = 99
        while len(x) > 0:
            a = x[0]
            x = x[1:]
            b = ord(a) - 77.5
            try:
                if abs(b) < 13:
                    c = b + 48.5 + y * c
                else:
                    c = int(a, 36) + y * c
            except Exception as e:
                c = 0
        return c

    def loop(self):
        """
        while (z++) try {
            eval(y.replace(/\b\w+\b/g, function(y) {
                return x[f(y, z) - 1] || ("_" + y)
            }));
            break
        }
        catch (_) {}
        """

        count = 0
        z = self.z() + 1
        while True:
            new_y = self.y
            self.pos = 0
            while self.pos < len(new_y):
                iter_y = new_y[self.pos:]
                found_one = False
                for m in re.finditer(r"\w+", iter_y):
                    found_one = True
                    y = m.group(0)
                    i = int(self.f(y, int(z))) - 1
                    if i >= len(self.x) or i < 0:
                        opt_1 = None
                    else:
                        opt_1 = self.x[i]
                    opt_2 = '_{0}'.format(y)
                    if opt_1 is None or str(opt_1) in ['0', 'False', '']:
                        opt_keep = opt_2
                    else:
                        opt_keep = opt_1
                    new_y = new_y[:self.pos] + iter_y[:m.start()] + opt_keep + iter_y[m.end():]
                    self.pos = self.pos + m.end() - len(y) + len(opt_keep)
                    break
                if not found_one:
                    z += 1
                    if new_y.startswith('var '):
                        return self.extract(new_y)
                    elif z > 1000:
                        return None
                    else:
                        break

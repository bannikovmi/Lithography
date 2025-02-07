from fractions import Fraction

class DrivePosition(Fraction):

    def to_improper(self):

        num = self.numerator
        den = self.denominator

        quot = num // den
        rem = num % den

        if rem == 0:
            return f"{quot}", ""
        else:
            if quot >= 0:
                return f"{quot}", f"{rem}/{den}"
            else:
                if quot == -1:
                    return f"{quot+1}", f"{rem-den}/{den}"
                else:
                    return f"{quot+1}", f"{den-rem}/{den}"

    def to_json(self):

        return [int(self.numerator), int(self.denominator)]
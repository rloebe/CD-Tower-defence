# Deník selhání AI – Matěj

Zápis každého případu, kdy AI udělala něco špatně a já to musel opravit. Podle zadání alespoň 3 případy. Jen skutečné případy, nejnovější dole.

## Případ 1: Hra se ze zipu nedala spustit podle návodu (23. 11. 2026)

- **Co jsem chtěl:** Stáhnout si hru do počítače a spustit ji, abych mohl testovat.
- **Co AI udělala špatně:** Poslala mi zip, ve kterém byla hra ještě jednou zabalená ve složce. Po „Extrahovat vše“ ve Windows tak vznikla složka ve složce (`CD-Tower-defence\CD-Tower-defence`). AI mi napsala, ať otevřu „složku CD-Tower-defence“, ale neupozornila, že jsou dvě a že soubory hry jsou až ve vnitřní.
- **Jak jsem to poznal:** Když jsem (po instalaci Pythonu) spustil instalaci knihoven, terminál napsal chybu `No such file or directory: 'requirements.txt'`. AI podle snímku obrazovky poznala, že jsem ve vnější složce.
- **Jak jsem to opravil:** Příkazem `cd CD-Tower-defence` jsem přešel do vnitřní složky a pak `py -m pip install -r requirements.txt` a `py src/main.py --okno` fungovaly.

## Případ 2: Moc otázek a dlouhých návodů místo práce (23. 11. 2026)

- **Co jsem chtěl:** Rychle dokončit projekt před termínem.
- **Co AI udělala špatně:** Pořád se mě ptala a dávala mi dlouhé návody, místo aby pokračovala v práci.
- **Jak jsem to poznal:** Zdržovalo mě to a nestíhal jsem.
- **Jak jsem to opravil:** Napsal jsem jí, ať přestane a pokračuje („everything GOOD move on“).

from PyQt6.QtWidgets import QComboBox
from typing import Iterable


class BetterDropDown(QComboBox):
    """This works just like the html equivalent where the displayed value isnt the real value of the label"""
    table: dict[str, str] = {}

    def __init__(self) -> None:
        super().__init__()

    def addItems(self, texts: Iterable[str], values: Iterable[str] | None = None) -> None:
        # create table to get the real value back later
        if values is None:
            values = texts
        for k, v in zip(texts, values):
            self.table[k] = v

        return super().addItems(texts)

    def currentText(self) -> str:
        current_text = super().currentText()
        if current_text not in self.table:
            raise ValueError
        return self.table[current_text]

    def setCurrentText(self, text: str | None) -> None:
        if text in self.table:
            super().setCurrentText(text)
        elif text in self.table.values():
            for k, v in self.table.items():
                if v == text:
                    super().setCurrentText(k)
                    break
        else:
            msg = f"value: {text} not in BetterDropDown!"
            raise ValueError(msg)
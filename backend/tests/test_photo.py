import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.generate import prepare_photo


def make_jpeg(width: int, height: int, orientation: int | None = None) -> bytes:
    image = Image.new("RGB", (width, height), "white")
    exif = Image.Exif()
    if orientation:
        exif[0x0112] = orientation  # tag EXIF « Orientation »
    output = io.BytesIO()
    image.save(output, format="JPEG", exif=exif)
    return output.getvalue()


def test_prepare_photo_reduit_a_1600_px() -> None:
    result = Image.open(io.BytesIO(prepare_photo(make_jpeg(4000, 3000))))
    assert result.size == (1600, 1200)
    assert result.format == "JPEG"


def test_prepare_photo_garde_les_petites_images() -> None:
    assert Image.open(io.BytesIO(prepare_photo(make_jpeg(800, 600)))).size == (800, 600)


def test_prepare_photo_redresse_selon_exif() -> None:
    # Orientation 6 = photo prise téléphone tourné : 4000x3000 stockée, 3000x4000 affichée
    result = Image.open(io.BytesIO(prepare_photo(make_jpeg(4000, 3000, orientation=6))))
    assert result.size == (1600, round(4000 * 1600 / 3000))
    assert 0x0112 not in result.getexif()  # métadonnées retirées


def test_route_from_photo_renvoie_le_texte_sans_rien_enregistrer(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("app.routers.lessons.transcribe_photo", lambda _: "La cellule est l'unité du vivant.")
    response = client.post("/lessons/from-photo", files={"photo": ("lecon.jpg", make_jpeg(100, 100), "image/jpeg")})
    assert response.status_code == 200
    assert response.json() == {"text": "La cellule est l'unité du vivant."}
    assert client.get("/lessons").json() == []


def test_route_from_photo_fichier_illisible_422(client: TestClient) -> None:
    response = client.post("/lessons/from-photo", files={"photo": ("lecon.jpg", b"pas une image", "image/jpeg")})
    assert response.status_code == 422
    assert response.json()["detail"] == "Ce fichier n'est pas une photo lisible."


def test_route_from_photo_sans_texte_422(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.routers.lessons.transcribe_photo", lambda _: "")
    response = client.post("/lessons/from-photo", files={"photo": ("lecon.jpg", make_jpeg(100, 100), "image/jpeg")})
    assert response.status_code == 422

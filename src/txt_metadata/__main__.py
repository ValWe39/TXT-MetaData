"""Point d'entrée : orchestration du pipeline et politique d'échec en
lot (FR-032, R9).

Codes retour : 0 = tout réussi ; 1 = au moins un échec ; 2 = erreur
fatale avant traitement (options invalides, clé absente, compteur
corrompu). Journalisation : progression et erreurs sur stderr, bilan
final sur stdout ; aucune donnée sensible n'est jamais affichée.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from . import batch, counter
from . import citation as citation_mod
from .cli import CliError, Options, parse_args
from .config import ConfigurationError, load_api_key
from .extract import create_client, extract_metadata
from .inputs import InputDocument, discover, pair_documents, read_text
from .models import DocumentResult, MetadataOutput
from .output import amend_in_place, load_existing, merge_amendment, write_new
from .sampling import build_extrait

COUNTER_FILENAME = Path("counter.txt")


def _verified(value: str, source_text: str) -> bool:
    """Vrai si la valeur est retrouvée dans le texte source (haut degré
    d'assurance pour l'amendement d'un champ déjà rempli, FR-026)."""
    if not value:
        return False
    needle = " ".join(value.split()).lower()
    haystack = " ".join(source_text.split()).lower()
    return needle in haystack


def _apply_amendment(
    existing: MetadataOutput,
    new: MetadataOutput,
    *,
    source_text: str,
) -> MetadataOutput:
    """Fusion d'amendement : les champs remplis ne sont challengés que
    si la nouvelle valeur est vérifiée mot à mot dans le texte source ;
    la typologie « Autre » (repli) peut être affinée."""
    verified = MetadataOutput(
        typologie=new.typologie,
        auteurs=[a for a in new.auteurs if _verified(a, source_text)],
        titre=new.titre if _verified(new.titre, source_text) else "",
        editeur=new.editeur if _verified(new.editeur, source_text) else "",
        date=new.date if _verified(new.date, source_text) else "",
        reference=new.reference if _verified(new.reference, source_text) else "",
        citation=new.citation
        if citation_mod.verify_in_text(new.citation, source_text)
        else "",
    )
    merged = merge_amendment(existing, verified, high_confidence=True)
    if existing.typologie != "Autre" and existing.typologie != new.typologie:
        merged.typologie = existing.typologie
    return merged


def process_document(
    doc: InputDocument,
    client: object,
    options: Options,
    *,
    counter_path: Path,
    log=None,
) -> DocumentResult:
    """Traite un document : lecture, échantillonnage, extraction,
    citation, puis création numérotée ou amendement sur place."""
    source_text = read_text(doc.path)
    extrait = build_extrait(source_text)
    metadata = extract_metadata(
        client,
        extrait,
        model_alias=options.model_alias,
        temperature=options.temperature,
        retries=options.retries,
        retry_delay=float(options.retry_time),
        sleep=time.sleep,
    )
    metadata.citation = citation_mod.resolve_citation(metadata, source_text=source_text)
    if doc.paired_json is not None:
        existing = load_existing(doc.paired_json)
        if existing is not None:
            merged = _apply_amendment(existing, metadata, source_text=source_text)
            amend_in_place(doc.paired_json, merged)
            if log:
                log(f"amendé sur place : {doc.paired_json}")
            return DocumentResult(
                source=str(doc.path), status="amended", detail=str(doc.paired_json)
            )
    occurrence = counter.next_occurrence(counter_path)
    target = write_new(
        metadata,
        output_dir=options.output_folder,
        input_path=doc.path,
        occurrence=occurrence,
    )
    if log:
        log(f"créé : {target}")
    return DocumentResult(source=str(doc.path), status="created", detail=str(target))


def _run(options: Options, *, counter_path: Path) -> tuple[list[DocumentResult], int]:
    documents = discover(options.paths)
    if not documents:
        print("Aucun fichier .md ou .txt à traiter.", file=sys.stderr)
        return [], 0
    pair_documents(documents)
    api_key = load_api_key()
    client = create_client(api_key)

    def log(message: str) -> None:
        print(message, file=sys.stderr)

    def worker(indexed: tuple[int, InputDocument]) -> DocumentResult:
        index, doc = indexed
        log(f"[{index + 1}/{len(documents)}] {doc.path.name} : traitement...")
        try:
            return process_document(
                doc, client, options, counter_path=counter_path, log=log
            )
        except Exception as exc:  # noqa: BLE001 - FR-032 : lot résilient
            log(f"[{index + 1}/{len(documents)}] {doc.path.name} : ÉCHEC : {exc}")
            return DocumentResult(
                source=str(doc.path), status="failed", detail=str(exc)
            )

    indexed = list(enumerate(documents))
    results = batch.run_batch(indexed, worker, batch_size=options.batch_size)
    return results, len(documents)


def _print_summary(results: list[DocumentResult], total: int) -> None:
    created = [r for r in results if r.status == "created"]
    amended = [r for r in results if r.status == "amended"]
    failed = [r for r in results if r.status == "failed"]
    print(
        f"Bilan : {len(created)} créé(s), {len(amended)} amendé(s), "
        f"{len(failed)} en échec, sur {total} document(s)."
    )
    for result in failed:
        print(f"  ÉCHEC {result.source} : {result.detail}")


def main(argv: list[str] | None = None) -> int:
    """Point d'entrée CLI (code retour 0/1/2)."""
    # console Windows : forcer l'UTF-8 pour afficher correctement les
    # accents (les fichiers de sortie sont déjà en UTF-8)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        options = parse_args(argv)
    except CliError as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 2
    try:
        counter.load(COUNTER_FILENAME)
    except counter.CounterError as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 2
    try:
        results, total = _run(options, counter_path=COUNTER_FILENAME)
    except ConfigurationError as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 2
    _print_summary(results, total)
    return 0 if all(r.status != "failed" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

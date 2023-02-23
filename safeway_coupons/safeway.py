from typing import List

from .accounts import Account
from .client import SafewayClient
from ._email import email_clip_results, email_error
from .errors import ClipError, Error, TooManyClipErrors
from .models import Offer, OfferStatus
from .utils import yield_delay, TARGET_OFFER_NAME
from .vons import clip_vons, return_vons_names

CLIP_ERROR_MAX = 5


class SafewayCoupons:
    def __init__(
        self,
        send_email: bool = True,
        debug_level: int = 0,
        sleep_level: int = 0,
        dry_run: bool = False,
        max_clip_count: int = 0,
        max_clip_errors: int = CLIP_ERROR_MAX,
    ) -> None:
        self.send_email = send_email
        self.debug_level = debug_level
        self.sleep_level = sleep_level
        self.dry_run = dry_run
        self.max_clip_count = max_clip_count
        self.max_clip_errors = max_clip_errors
        self.email_already_sent = False

    def clip_for_account(self, account: Account) -> None:
        print(f"Clipping coupons for Safeway account {account.username}")
        swy = SafewayClient(account)
        clipped_offers: List[Offer] = []
        clip_errors: List[ClipError] = []
        try:
            offers = swy.get_offers()
            unclipped_offers = [
                o for o in offers if o.status == OfferStatus.Unclipped
            ]
            offer_names = [o.name for o in unclipped_offers]
            offer_names_vons = return_vons_names(account.username, account.password)
            if TARGET_OFFER_NAME not in offer_names:
                print("$5 not found.")
                if self.email_already_sent:
                    return
                elif 'Any O Organics Product' not in offer_names or 'Any Produce Dept. Purchase' not in offer_names or \
                        'Any O Organics Product' not in offer_names_vons or 'Any Produce Dept. Purchase' not in offer_names_vons:
                    return
            if not unclipped_offers:
                print("All the coupons have been clipped.")
                return
            rjust_size = len(str(len(unclipped_offers)))
            for i, offer in enumerate(
                yield_delay(
                    unclipped_offers, self.sleep_level, self.debug_level
                )
            ):
                progress_count = (
                    f"({str(i + 1).rjust(rjust_size, ' ')}"
                    f"/{len(unclipped_offers)}) "
                )
                try:
                    if not self.dry_run:
                        swy.clip(offer)
                    print(f"{progress_count} Clipped {offer}")
                    clipped_offers.append(offer)
                    if (
                        self.max_clip_count
                        and len(clipped_offers) >= self.max_clip_count
                    ):
                        print(
                            "Clip maximum count of "
                            f"{self.max_clip_count} reached"
                        )
                        break
                except ClipError as e:
                    print(f"{progress_count} {e}")
                    clip_errors.append(e)
                    if (
                        self.max_clip_errors
                        and len(clip_errors) >= self.max_clip_errors
                    ):
                        raise TooManyClipErrors(
                            e,
                            clipped_offers=clipped_offers,
                            errors=clip_errors,
                        )
            clip_vons(account.username, account.password)
            print(f"Clipped {len(clipped_offers)} coupons")
            email_clip_results(
                account,
                clipped_offers,
                error=None,
                clip_errors=clip_errors,
                debug_level=self.debug_level,
                send_email=self.send_email and not self.dry_run,
            )
            self.email_already_sent = True
        except Error as e:
            email_error(
                account,
                error=e,
                debug_level=self.debug_level,
                send_email=self.send_email and not self.dry_run,
            )
            raise

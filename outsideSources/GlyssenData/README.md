# SIL Glyssen Data

The original copy of these files came from the code repository at
https://github.com/sillsdev/Glyssen
and especially from https://github.com/sillsdev/Glyssen/tree/master/GlyssenEngine/Resources and
https://github.com/sillsdev/Glyssen/tree/master/DevTools/Resources.
Glyssen is a C# program with a MIT License,
although that is indeed more of a software code licence than a data one.
The stated purpose of the program is
"Produce high-quality dramatized audio recordings of Scripture".

Last downloaded: 2022-07-25

The original files were released under a MIT license.

These copies are simply included here for convenience so we can easily monitor
exactly which data the JSON and other files were derived from.
It you are aware that our copy has become outdated,
please contact us.

We would like to express grateful thanks to SIL for this work,
and especially to Tom Bogle and others
that contributed to make their work available under an open licence.

Any work or effort that has been contributed by Freely-Given.org
processing these data files is freely gifted to the world,
i.e, our curation work is released into the public domain.
(Please note that that does not at all imply that the
licence conditions of the original content creators no longer apply.)

## Notes

- CharacterDetail.tsv (renamed from .txt) contains 1,266 data rows with columns:
  - Character ID
  - Max Speakers
  - Gender
  - Age
  - Status
  - Comment
  - Reference
  - FCBH Character
- CharacterVerse.tsv (renamed from .txt) contains almost 21,000 data rows with columns:
  - C
  - V
  - Character ID
  - Delivery
  - Alias
  - Quote Type
  - Default Character
  - Parallel Passage
- original_CharacterNames_BookChapterVerse.txt contains 10,885 lines like:
  - 2PE 1.0 character=narrator-2PE
  - 1CO 9.9 character=scripture
  - 1JN 2.18 character=John
  - 1JN 2.4 character=man who says 'I know him'
  - 1JN 2.6 character=man who says 'we remain in union with God'
  - 1JN 4.20 character=anyone
  - 1JN 4.21 character=Jesus
  - 1KI 1.11 character=Nathan, the prophet
  - 1KI 1.16 character=David, king [very old]
- StyleToCharacterMappings.xml maps USFM/USX character styles to characters. The complete file is:
```
<?xml version="1.0" encoding="utf-16"?>
<StyleToCharacterMappings>
    <StyleMapping sf="wj" character="Jesus"/>
    <StyleMapping sf="qt" character="scripture"/>
    <StyleMapping sf="d" paragraph="true" character="Narrator"/>
    <StyleMapping sf="qa" paragraph="true" character="BookOrChapter"/>
</StyleToCharacterMappings>
```

## Formats

...

## Notes on QuoteType

This is C# code and comments extracted from CharacterVerse.cs.

```
public enum QuoteType
{
    /// <summary>
    /// Normal speech expected to be marked up using quotation marks in the text (this
    /// can include both dialogue as well as other forms of spoken discourse, but quotes that
    /// are commonly marked up as dialog (in writing systems that distinguish between dialogue
    /// and other forms of spoken discourse) will typically be identified as Dialogue.
    /// </summary>
    Normal,

    /// <summary>
    /// Used for speech in passages that are known to be spoken by a particular character
    /// and can be assigned as such even if no punctuation is present to indicate the spoken
    /// discourse. (In some translations, quotation marks may be omitted in text marked as
    /// poetry or in long speeches, especially where the speeches contain other nested quotations
    /// that might make explicit use of first-level quotation marks more unwieldy.
    /// </summary>
    Implicit,

    /// <summary>
    /// Like <seealso cref="Implicit"/>, but when a verse also has the possibility of a self-quote.
    /// Knowing this makes it possible for us to ignore quoted text within the larger discourse and
    /// not incorrectly assume that explicit quotes are being used (along with a "he said" reporting
    /// clause) in the verse. (As noted in the quote parser, there is a slight chance a stray
    /// "he said" could mess us up here, but that's unlikely.)
    /// </summary>
    ImplicitWithPotentialSelfQuote,

    /// <summary>
    /// Conversation between two or more characters, generally consisting of relatively short
    /// exchanges. (Some writing systems use punctuation to distinguish between dialogue
    /// and other forms of spoken discourse.)
    /// </summary>
    Dialogue,

    /// <summary>
    /// Speech that is commonly rendered in an indirect way rather than as a direct quote.
    /// Since quotation marks were not in use when the Bible was written, this distinction is
    /// not based on the original languages. The decision about whether to render a particular
    /// piece of spoken discourse as direct or indirect speech will tend to vary from language
    /// to language, and some languages simply do not allow for indirect speech at all. Quotes
    /// marked as Indirect will not be considered as "expected" quotes.
    /// </summary>
    Indirect,

    /// <summary>
    /// Potential direct speech that is
    /// a) in verses that are not found in some manuscripts and may be omitted from translations;
    /// b) likely to be marked up using poetry but without quotes;
    /// c) likely not to be marked as speech at all, but in these cases <seealso cref="Rare"/> is
    /// probably a better choice.
    /// d) A self-quote by the narrator (especially where the narrator refers to himself in the
    /// first person). * ENHANCE: We might want to consider breaking this case out into a
    /// distinct type.
    /// e) In verses where the text could be read by the narrator but there is also a reasonable
    /// narrator override, the non-narrator option(s) will be listed as potential speakers, so
    /// scripter can choose the override character if so desired.
    /// For now, Potential quotes will be treated just like <seealso cref="Indirect"/> quotes --
    /// they will not be considered as "expected" quotes.
    /// </summary>
    Potential,

    /// <summary>
    /// Speech not attributed to a real, historical figure. This includes things that someone
    /// might say, predicted future speech*, hypothetical words expressing an attitude held
    /// by a group, words attributed to personified objects, etc. *Note: future speech attributed
    /// to a character in the context of a narrative-style vision (that can be presented
    /// dramatically) need not be regarded as hypothetical.
    /// </summary>
    Hypothetical,

    /// <summary>
    /// Quotations of actual past speech or written words, proverbs, etc. OR something a person or
    /// group is commanded to speak. Typically, these can be read by the narrator, though in some
    /// cases it may be useful to use another voice and/or special sound effects. When spoken by
    /// the narrator, a "Quotation" can also be a place where quotation marks are likely to be used
    /// for something other than speech (e.g., a translation, a foreign phrase, a title, or a literal
    /// name). For dramatic effect, it might sometimes be appropriate to have the person being
    /// quoted or commanded to speak actually speak the words (especially if it is a command to say
    /// something immediately (e.g., when God tells Moses or a prophet to say something). This quote
    /// type is used any place where the reference text dramatizes this kind of second-level speech.
    /// See also, <seealso cref="Alternate"/>
    /// </summary>
    Quotation,

    /// <summary>
    /// Technically not a "quote type" per se - rather, this is a special case of where a quote can be
    /// interrupted (i.e., by the narrator) using a parenthetical remark. For example, in MAT 24:15 or
    /// MRK 13:14, where it says: (let the reader understand). Technically, it is probably better for
    /// the quote to be explicitly ended and re-opened, but it is not uncommon for translators to leave
    /// these kinds of interruptions inside the surrounding direct speech. Because these are not easy
    /// to identify unambiguously and there are different ideas about how best to dramatize them, they
    /// will always be marked as ambiguous so the user has a chance to evaluate them and decide what to do.
    /// </summary>
    Interruption,

    /// <summary>
    /// Used to indicate a possible alternate speaker for dramatization purposes. This is normally used in
    /// prophetic works or other places where speech is attributed to both the original speaker and the
    /// prophet, spokesperson, or announcer. As opposed to <seealso cref="Quotation"/>, which normally
    /// indicates past speech, this quote type is used to distinguish between the character presumed to be
    /// the preferred speaker and an alternate speaker who could legitimately speak the same lines but is
    /// not expected to (based on the decision reflected by the reference text). Hence, Glyssen will
    /// automatically assign the quoted text to the preferred character and never to the alternate, but the
    /// alternate will be listed as an option in Identify Speaking Parts, in case the scripter wants to
    /// choose that character instead. This makes it possible to avoid ambiguity for the vast number of
    /// passages where there is a single well-defined quote and the ambiguity is merely a dramatization
    /// decision. (Basically, the effect is the same as using <seealso cref="Hypothetical"/>, except without
    /// the performance hit to look in the reference text to see whether the alternate character is used.
    /// This type can also be used when there is a potential quote that spills over into a subsequent verse
    /// that has an actual expected quote. Some translations (e.g., ISV) wrap virtually the entire text in
    /// quotes to indicate that the prophet is speaking all the text. In these cases, the actual quote may
    /// be second level. For translations that do not do this, we don't want the prophet to accidentally be
    /// considered as a candidate for the quoted text (which would result in an ambiguity). By using the
    /// Alternate quote type, we ensure that it will only be considered for an on-going quote that was
    /// opened in a previous verse.
    /// </summary>
    Alternate,

    /// <summary>
    /// Used to indicate a potential speaker which so very rarely occurs in any project that it cannot
    /// be safely assigned automatically. Typically, this kind of quote represents an attitude, thought,
    /// intention, desire, or belief. In the target language, this may be expressed as actual speech, in
    /// which case it should definitely be dramatized. But it might just be an unexpressed thought,
    /// spelled out literally for the sake of the audience, in which case, the target community will
    /// need to decide whether to dramatize it or have it read by the narrator. If a verse has only Rare quotes and the parser finds a
    /// quote in that verse, it will be regarded as unexpected, but in Identify Speaking Parts, the rare
    /// speaker(s) will appear (along with the narrator) in the list of choices. So at least for now,
    /// the actual handling will be identical to <seealso cref="Alternate"/>, though it is a semantically
    /// distinct case. See PG-1233 for a full discussion, along with an alternate proposal for how to
    /// handle Rare when it occurs along with other quote types in a verse.
    /// </summary>
    Rare,
}
```

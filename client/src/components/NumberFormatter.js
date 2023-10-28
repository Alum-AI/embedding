export default function NumberFormat({ number, locale = "en-US" }) {
  return new Intl.NumberFormat(locale).format(number);
}

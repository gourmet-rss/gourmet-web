import classNames from "classnames";
import { feedGridClass } from "./page";

export default function Loading() {
  return (
    <div className={classNames(feedGridClass, "w-full")}>
      {new Array(12).fill(null).map((_, i) => (
        <div key={i} className="skeleton w-full h-[400px]"></div>
      ))}
    </div>
  );
}

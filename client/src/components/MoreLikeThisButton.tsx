import newFlavourFromContentId from "@/app/actions/newFlavourFromContentId";
import classNames from "classnames";
import { Sparkles } from "lucide-react";
import { useActionState } from "react";

export default function MoreLikeThisButton({
  contentId,
}: {
  contentId: number;
}) {
  const [, formAction, isCreatingFlavour] = useActionState(
    newFlavourFromContentId.bind(null, contentId),
    null,
  );

  return (
    <form action={formAction} className="tooltip" data-tip="More this flavour">
      <button
        className={classNames(
          `p-1.5 rounded-full transition-colors text-gray-500 hover:text-purple-600 hover:bg-purple-50 dark:text-gray-400 dark:hover:text-purple-400 dark:hover:bg-purple-900/20`,
          {
            loading: isCreatingFlavour,
          },
        )}
        aria-label="More of this flavour"
      >
        <Sparkles size={18} />
      </button>
    </form>
  );
}
